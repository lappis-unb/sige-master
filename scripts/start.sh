#!/bin/bash

# Exporting all environment variables to use in crontab
env | sed 's/^\(.*\)$/ \1/g' > /root/env

while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -q -U $POSTGRES_USER; do
  >&2 echo "Postgres is unavailable - sleeping...";
  sleep 5;
done;
>&2 echo "Postgres is up - executing commands...";

echo '======= RUNNING PIP INSTALL'
pip install --no-cache-dir -r requirements.txt

echo '======= MAKING MIGRATIONS'
python3 manage.py makemigrations

echo '======= RUNNING MIGRATIONS'
python3 manage.py migrate

echo '======= RUNNING SEED'
python3 seed_db.py

echo '======= RUNNING SERVER'
python3 manage.py runserver 0.0.0.0:8001
