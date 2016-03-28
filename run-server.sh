#!/bin/sh -e

if [ "z$HOST" = "z" ]; then
    HOST="0.0.0.0"
fi

if [ "z$PORT" = "z" ]; then
    PORT=8000
fi

/usr/local/bin/gunicorn metadataproxy:app --workers=2 -k gevent -b $HOST:$PORT
