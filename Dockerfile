FROM lyft/gunicorn:1e21b48c70e80b2853a53ea455380c49e2d87959
COPY requirements.txt /code/metadataproxy/requirements.txt
RUN /code/containers/python/pip-installer /code/metadataproxy/requirements.txt
COPY . /code/metadataproxy/
