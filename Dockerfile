FROM lyft/gunicorn:df28a20af3e2ea3d006859b4da2034d36d4fa028
COPY requirements.txt /code/metadataproxy/requirements.txt
RUN /code/containers/python/pip-installer /code/metadataproxy/requirements.txt
COPY . /code/metadataproxy/
