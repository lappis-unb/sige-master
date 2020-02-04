#!/bin/bash

mkdir -p locale
mkdir -p locale/en
mkdir -p locale/pt_BR
django-admin makemessages --all --ignore venv
django-admin compilemessages --ignore venv --ignore env
