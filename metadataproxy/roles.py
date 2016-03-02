# Import python libs
import datetime
import dateutil.tz
import json
import socket
import re
import logging

# Import third party libs
import boto3
import docker
import docker.errors
from botocore.exceptions import ClientError

# Import metadataproxy libs
from metadataproxy import app

ROLES = {}
CONTAINER_MAPPING = {}
_docker_client = None
_iam_client = None
_sts_client = None

if app.config['ROLE_MAPPING_FILE']:
    with open(app.config.get('ROLE_MAPPING_FILE'), 'r') as f:
        ROLE_MAPPINGS = json.loads(f.read())
else:
    ROLE_MAPPINGS = {}


def docker_client():
    global _docker_client
    if _docker_client is None:
        _docker_client = docker.Client(base_url=app.config['DOCKER_URL'])
    return _docker_client


def iam_client():
    global _iam_client
    if _iam_client is None:
        _iam_client = boto3.client('iam')
    return _iam_client


def sts_client():
    global _sts_client
    if _sts_client is None:
        _sts_client = boto3.client('sts')
    return _sts_client


def find_container(ip):
    pattern = re.compile(app.config['HOSTNAME_MATCH_REGEX'])
    client = docker_client()
    if ip in CONTAINER_MAPPING:
        try:
            return client.inspect_container(CONTAINER_MAPPING[ip])
        except docker.errors.NotFound:
            del CONTAINER_MAPPING[ip]
    if app.config['ROLE_REVERSE_LOOKUP']:
        try:
            _fqdn = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            pass
    # TODO: cache id -> container data in an LRU
    _ids = [c['Id'] for c in client.containers()]
    for _id in _ids:
        try:
            c = client.inspect_container(_id)
        except docker.errors.NotFound:
            continue
        _ip = c['NetworkSettings']['IPAddress']
        if ip == _ip:
            return c
        if app.config['ROLE_REVERSE_LOOKUP']:
            hostname = c['Config']['Hostname']
            domain = c['Config']['Domainname']
            fqdn = '{0}.{1}'.format(hostname, domain)
            # Default pattern matches _fqdn == fqdn
            _groups = re.match(pattern, _fqdn).groups()
            groups = re.match(pattern, fqdn).groups()
            if _groups and groups:
                if groups[0] == _groups[0]:
                    return c
    return None


def get_role_name_from_ip(ip):
    if app.config['ROLE_MAPPING_FILE']:
        return ROLE_MAPPINGS.get(ip, app.config['DEFAULT_ROLE'])
    container = find_container(ip)
    if container:
        env = container['Config']['Env']
        for e in env:
            key, val = e.split('=', 1)
            if key == 'IAM_ROLE':
                return val
        return app.config['DEFAULT_ROLE']
    else:
        return None


def get_role_info_from_ip(ip):
    role_name = get_role_name_from_ip(ip)
    if not role_name:
        return {}
    try:
        role = get_role(role_name)
    except GetRoleError:
        logging.exception('Failed to get role {0}.'.format(role_name))
        return {}
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    now = datetime.datetime.now(dateutil.tz.tzutc())
    return {
        'Code': 'Success',
        # TODO: This is probably not the right thing to return here.
        'LastUpdated': now.strftime(time_format),
        'InstanceProfileArn': role['Role']['Arn'],
        'InstanceProfileId': role['Role']['RoleId']
    }


def _get_credential_reponse(assumed_role):
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    credentials = assumed_role['Credentials']
    expiration = credentials['Expiration']
    updated = expiration - datetime.timedelta(minutes=60)
    return {
        'Code': 'Success',
        'LastUpdated': updated.strftime(time_format),
        'Type': 'AWS-HMAC',
        'AccessKeyId': credentials['AccessKeyId'],
        'SecretAccessKey': credentials['SecretAccessKey'],
        'Token': credentials['SessionToken'],
        'Expiration': expiration.strftime(time_format)
    }


def get_role(role_name):
    iam = iam_client()
    try:
        role = iam.get_role(RoleName=role_name)
    except ClientError as e:
        should_raise = True
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
            if app.config['DEFAULT_ROLE']:
                role = iam.get_role(RoleName=app.config['DEFAULT_ROLE'])
                should_raise = False
        if should_raise:
            response = e.response['ResponseMetadata']
            raise GetRoleError((response['HTTPStatusCode'], e.message))
    return role


def get_assumed_role(requested_role, api_version='latest'):
    if requested_role in ROLES:
        assumed_role = ROLES[requested_role]
        expiration = assumed_role['Credentials']['Expiration']
        now = datetime.datetime.now(dateutil.tz.tzutc())
        expire_check = now + datetime.timedelta(minutes=5)
        if expire_check < expiration:
            return _get_credential_reponse(assumed_role)
    role = get_role(requested_role)
    sts = sts_client()
    assumed_role = sts.assume_role(
        RoleArn=role['Role']['Arn'],
        RoleSessionName='devproxyauth'
    )
    ROLES[role['Role']['RoleName']] = assumed_role
    return _get_credential_reponse(assumed_role)


class GetRoleError(Exception):
    pass
