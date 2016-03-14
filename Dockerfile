FROM lyft/gunicorn:dda7a403c7a43e9752262be507e097912af4a861
COPY requirements.txt /code/metadataproxy/requirements.txt
RUN /code/containers/python/pip-installer /code/metadataproxy/requirements.txt
COPY . /code/metadataproxy/
