FROM lyft/gunicorn:e4c7537168fa1959780629ce89d918cbbea3fc65
COPY requirements.txt /code/metadataproxy/requirements.txt
RUN /code/containers/python/pip-installer /code/metadataproxy/requirements.txt
COPY . /code/metadataproxy/
