#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

set -o allexport
source .env set
+o allexport

echo $PORT
PORT="${PORT:-8080}"
echo $PORT
exec uvicorn webapp.main:app --host 0.0.0.0 --port "$PORT"
# exec find / -name uvicorn 2> /dev/null
