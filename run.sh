#!/bin/bash

if [ "$VIRTUAL_ENV" == "" ]; then
    echo "ERROR: You must be in a VENV to run this script"
    exit 1
else
    # Install node dependencies for transpiling
    cd frontend
    npm install
    npm run build

    cd ../
    docker compose up database -d

    cd ../passwordmanager
    # typical django startup routine
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic --noinput
    python manage.py runserver

fi