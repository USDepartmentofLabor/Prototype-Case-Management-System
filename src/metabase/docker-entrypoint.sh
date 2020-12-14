#!/bin/sh
apk update && apk add python3
python3 -m pip install -U pip
python3 -m pip install requests
python3 init.py &
exec bash /app/run_metabase.sh
