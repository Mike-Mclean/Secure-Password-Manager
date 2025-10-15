#!/bin/bash

# docker-compose run --rm project bash -c "
#   set -e
#   pip install --user -r requirements.txt
#   python manage.py test --settings passwordmanager.settings
# "
ORIGINAL_DIR=$(pwd)
cleanup() {
    cd "$ORIGINAL_DIR"
}

trap cleanup ERR INT EXIT

./.venv/bin/python passwordmanager/manage.py migrate --settings=passwordmanager.settings.unittests
./.venv/bin/python passwordmanager/manage.py test tests --settings=passwordmanager.settings.unittests
