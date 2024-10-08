#!/usr/bin/env bash

# SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# cd "$SCRIPT_DIR" || exit

# set -o allexport
# source .env set
# +o allexport

exec python nbastats/manage.py scrape