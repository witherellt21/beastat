#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR" || exit

set -o allexport
source .env set
+o allexport

PORT="${PORT:-8080}"
exec uvicorn app:app --host 0.0.0.0 --port "$PORT"
# exec find / -name uvicorn 2> /dev/null
