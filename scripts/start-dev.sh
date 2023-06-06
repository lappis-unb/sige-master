#!/bin/bash
set -e errexit
set -e pipefail
set -e nounsetcle
set -e xtrace

C='\e[0;36m'     # cyan
Y='\033[0;33m'   # yellow
G='\033[0;32m'   # green 
B='\033[0;34m'   # blue
W='\033[0;37m'   # white
E='\033[0m'      # end

DB_NAME="$POSTGRES_DB"
DB_HOST="$POSTGRES_HOST"
DB_USERNAME="$POSTGRES_USER"
DB_PASSWORD="$POSTGRES_PASSWORD"

# Exporting all environment variables to use in crontab
env | sed 's/^\(.*\)$/ \1/g' > /root/env

sleep 5 # wait 5 seconds initial startup before starting the server
echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> WAIT POSTGRES DB TO BE READY"
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USERNAME" -c '\q'; do
  >&2 echo "${Y}Postgres is unavailable - sleeping..."
  sleep 2
done
echo "${G}Postgres is ready!"

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> CHECK INTEGRITY (check)                                                                                                  ${E}"
python manage.py check
                                                                                                       
echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> MAKING MIGRATIONS (makemigrations)                                                                                       ${E}" 
python manage.py makemigrations

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> APPLYING MIGRATIONS (migrate)                                                                                            ${E}"
python manage.py migrate

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> STARTING CRON                                                                                                            ${E}"
echo 'Cronjobs sige-cron in operating system'
/bin/cp /sige-master/crons/cronjob /etc/cron.d/sige-cron
crontab /etc/cron.d/sige-cron
cron

cronitor list /etc/cron.d/sige-cron

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo '\e[33;36m=> RUNNING SERVER (runserver) \e[0;33m                                                                            _        '
echo '\e[1;33m                                                       ۞          ___ _  __ _  ___    _ __ ___   __ _ ___| |_ ___ _ __     '
echo '\e[1;33m                                                     ۞   ۞       / __| |/ _` |/ _ \  | `_ ` _ \ / _` / __| __/ _ \ `__|    '
echo '\e[1;33m                                                   ۞   ۞   ۞     \__ \ | (_| |  __/  | | | | | | (_| \__ \ ||  __/ |      '
echo '\e[1;33m                                                     ۞   ۞       |___/_|\__, |\___|  |_| |_| |_|\__,_|___/\__\___|_|       '
echo '\e[1;33m                                                       ۞                |___/                                              ' 
echo "Starting ${W}"${API_NAME}"${E} - ${G}http://"${API_HOST}":${API_PORT}${E}                                             ${B}UnB ${Y}Energia   "
echo "         ${W}${DB_HOST}${E}  - ${Y}http://"${API_HOST}":${POSTGRES_PORT}${E}                                                      ${B}Eficiencia Energetica"
echo "${C}____________________________________________________________________________________________________________________________${E}"
python manage.py runserver ${API_HOST}:${API_PORT}
