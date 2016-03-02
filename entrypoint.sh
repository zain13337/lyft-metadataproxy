#!/bin/bash
set -e

if [ ! -z "$DEVBOX" ]; then
  export MOCK_API="true"
  export MOCKED_INSTANCE_ID="onebox"
fi

cd /code/metadataproxy
exec /code/containers/gunicorn/launcher wsgi:app --bind 0.0.0.0:45001
