import re
import logging

from flask import Response
from flask import request
from flask import redirect
from flask import stream_with_context
from flask import jsonify

import requests

from metadataproxy import app
from metadataproxy import roles


@app.route('/<path:url>')
def home(url):
    pattern = re.compile('^/(.+?)/meta-data/iam/info$')
    match = re.match(pattern, '/{0}'.format(url))
    if match:
        return jsonify(roles.get_role_info_from_ip(request.remote_addr))
    pattern = re.compile('^/(.+?)/meta-data/iam/security-credentials$')
    match = re.match(pattern, '/{0}'.format(url))
    if match:
        return redirect(
            '{0}/{1}/'.format(app.config['METADATA_URL'], url),
            code=301
        )
    pattern = re.compile('^/(.+?)/meta-data/iam/security-credentials/$')
    match = re.match(pattern, '/{0}'.format(url))
    if match:
        return roles.get_role_name_from_ip(request.remote_addr)
    pattern = re.compile('^/(.+?)/meta-data/iam/security-credentials/(.*)$')
    match = re.match(pattern, '/{0}'.format(url))
    if match:
        logging.debug('Matched security credentials request url.')
        ip_role_match = roles.get_role_name_from_ip(request.remote_addr)
        if ip_role_match != match.groups()[1]:
            return '', 404
        assumed_role = roles.get_assumed_role(
            requested_role=match.groups()[1],
            api_version=match.groups()[0]
        )
        return jsonify(assumed_role)

    logging.debug('Did not match credentials request url; passing through.')
    req = requests.get(
        '{0}/{1}'.format(app.config['METADATA_URL'], url),
        stream=True
    )
    return Response(
        stream_with_context(req.iter_content()),
        content_type=req.headers['content-type']
    )
