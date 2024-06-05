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

# Exporting all environment variables to use in crontab
env | sed 's/^\(.*\)$/ \1/g' > /root/env

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> WAIT POSTGRES DB TO BE READY"
sleep 3 # wait 5 seconds initial startup before starting the server
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -c '\q'; do
  >&2 echo "\n${Y}Postgres is unavailable - sleeping...\n"
  sleep 1
done
echo
echo "${G}Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> CREATING LOGS DIRECTORY                                                                                                  ${E}"
mkdir -p /sige-master/logs/tasks
mkdir -p /sige-master/logs/apps
chmod -R 777 /sige-master/logs

if [ -d "/sige-master/logs" ]; then
  echo "- Tasks directory: /sige-master/logs/tasks"
  echo "- Apps directory: /sige-master/logs/apps"
  echo "${G}Logs directory created successfully!"
else
  echo "${Y}Logs directory not created!"
fi

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> CHECK INTEGRITY (check)                                                                                                  ${E}"
python manage.py check

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> COLLECTING STATIC FILES (collectstatic)                                                                                 ${E}"
python manage.py collectstatic --noinput
                                                                                                       
echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> MAKING MIGRATIONS (makemigrations)                                                                                       ${E}" 
python manage.py makemigrations --noinput

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> APPLYING MIGRATIONS (migrate)                                                                                            ${E}"
python manage.py migrate --noinput

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> CREATING SUPERUSER                                                                                                       ${E}"
python manage.py create_admin

echo "${C}____________________________________________________________________________________________________________________________${E}"
echo "${C}=> POPULATING DATABASE (custom command)                                                                                           ${E}"
python manage.py populate_states

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
echo "         ${W}${POSTGRES_HOST}${E}  - ${Y}http://"${API_HOST}":${POSTGRES_PORT}${E}                                                      ${B}Eficiencia Energetica"
echo "${C}____________________________________________________________________________________________________________________________${E}"
python manage.py runserver ${API_HOST}:${API_PORT}
# python manage.py runserver_plus ${API_HOST}:${API_PORT}
