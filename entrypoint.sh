#!/bin/bash
set -e
if [ ! -z "$DEVBOX" ]; then
  export MOCK_API="true"
  export MOCKED_INSTANCE_ID="onebox"
fi
exec gunicorn wsgi:app --bind 0.0.0.0:45001
