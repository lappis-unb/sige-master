FROM python:3.6

RUN apt-get update && \
    apt-get install -y libpq-dev \
                       cron

WORKDIR /smi-master

COPY . /smi-master

# Setting cron
COPY crons/crontab /etc/cron.d/smi-cron

RUN chmod 0644 /etc/cron.d/smi-cron

RUN touch /var/log/cron.log

RUN /usr/bin/crontab /etc/cron.d/smi-cron

RUN pip install --no-cache-dir -r requirements.txt

CMD ['echo '======= RUNNING SEED'']
CMD ['python', 'seed_db.py']
