FROM lyft/gunicorn:20c5d7c09dce1c6f7acaa34e0b6ec7434815500f
COPY requirements.txt /code/metadataproxy/requirements.txt
RUN /code/containers/python/pip-installer /code/metadataproxy/requirements.txt
COPY . /code/metadataproxy/
