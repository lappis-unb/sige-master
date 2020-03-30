#!/bin/bash

# Exporting all environment variables to use in crontab
env | sed 's/^\(.*\)$/ \1/g' > /root/env

echo '======= CHECKING FOR UNINSTALLED PKGs AND INSTALLING'
pip freeze || pip install -r requirements.txt

echo "======= POSTGRES IS UP, CONNECTING"

echo '======= RUNNING PIP INSTALL'
pip install --no-cache-dir -r requirements.txt

echo '======= MAKING MIGRATIONS'
python3 manage.py makemigrations

echo '======= RUNNING MIGRATIONS'
python3 manage.py migrate

echo '======= RUNNING SEED'
python3 seed_db.py

echo '======= STARTING CRON'
cron

echo '======= RUNNING SERVER'
python3 manage.py runserver 0.0.0.0:8001
