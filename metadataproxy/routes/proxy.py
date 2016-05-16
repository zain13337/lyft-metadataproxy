import re

from flask import Response
from flask import request
from flask import redirect
from flask import stream_with_context
from flask import jsonify

import requests

from metadataproxy import app
from metadataproxy import log
from metadataproxy import roles

@app.route('/<api_version>/meta-data/iam/info')
def iam_role_info(api_version):
    role_name_from_ip = roles.get_role_name_from_ip(request.remote_addr)
    if role_name_from_ip:
        log.debug('Providing IAM role info for {0}'.format(role_name_from_ip))
        return jsonify(roles.get_role_info_from_ip(request.remote_addr))
    else:
        log.error('Role name not found; returning 404.')
        return '', 404

@app.route('/<api_version>/meta-data/iam/security-credentials/')
def iam_role_name(api_version):
    role_name_from_ip = roles.get_role_name_from_ip(request.remote_addr)
    if role_name_from_ip:
        return role_name_from_ip
    else:
        log.error('Role name not found; returning 404.')
        return '', 404

@app.route('/<api_version>/meta-data/iam/security-credentials/<role_name>')
def iam_sts_credentials(api_version, role_name):
    role_name_from_ip = roles.get_role_name_from_ip(request.remote_addr)
    if role_name_from_ip != role_name:
        msg = "Role name {0} doesn't match expected role for container {1}"
        log.error(msg.format(role_name, role_name_from_ip))
        return '', 404
    log.debug('Providing assumed role credentials for {0}'.format(role_name))
    assumed_role = roles.get_assumed_role(
        requested_role=role_name,
        api_version=api_version
    )
    return jsonify(assumed_role)

@app.route('/<path:url>')
@app.route('/')
def passthrough(url=''):
    log.debug('Did not match credentials request url; passing through.')
    req = requests.get(
        '{0}/{1}'.format(app.config['METADATA_URL'], url),
        stream=True
    )
    return Response(
        stream_with_context(req.iter_content()),
        content_type=req.headers['content-type']
    )
