#!/usr/bin/env bash

if [ -z "$1" ]
  then echo "Usage: check.sh <URL>" && exit 1
fi

# Automatically exit on error
set -e

# Ping the desired URL, fail if not 2xx
curl -s --fail $1 > /dev/null

echo "OK"
