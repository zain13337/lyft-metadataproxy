FROM lyft/gunicorn:aa4c10137c420875049d12c48d0c9bd07fc495d1
COPY requirements.txt /code/metadataproxy/requirements.txt
RUN /code/containers/python/pip-installer /code/metadataproxy/requirements.txt
COPY . /code/metadataproxy/
