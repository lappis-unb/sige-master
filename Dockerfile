FROM python:3.6

RUN apt-get update && \
    apt-get install -y postgresql \
                       postgresql-client \
                       libpq-dev\
                       cron

WORKDIR /smi-master

COPY . /smi-master

RUN pip install --no-cache-dir -r requirements.txt
