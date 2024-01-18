FROM python:3.11.2-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    postgresql-client \
    locales \
    gettext \
    iputils-ping \
    net-tools \
    dnsutils \
    curl \
    wget\
    locales &&\
    apt-get autoremove -y &&\
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /sige-master
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /sige-master

# ----------------------------< locale and timezone >-------------------------------------
RUN sed -i 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen &&\
    locale-gen pt_BR.UTF-8 &&\
    dpkg-reconfigure --frontend noninteractive locales &&\
    ln -snf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime &&\ 
    echo "America/Sao_Paulo" > /etc/timezone &&\
    dpkg-reconfigure -f noninteractive tzdata


# --------------------------------< logrotate >-------------------------------------------
RUN mkdir -p /etc/logrotate.d && \
    touch /sige-master/logs/cron_output.log && \
    echo "/sige-master/logs/cron_output.log {" > /etc/logrotate.d/sige_master && \
    echo "  size 100M" >> /etc/logrotate.d/sige_master && \
    echo "  daily" >> /etc/logrotate.d/sige_master && \
    echo "  missingok" >> /etc/logrotate.d/sige_master && \
    echo "  rotate 7" >> /etc/logrotate.d/sige_master && \
    echo "  compress" >> /etc/logrotate.d/sige_master && \
    echo "  delaycompress" >> /etc/logrotate.d/sige_master && \
    echo "  notifempty" >> /etc/logrotate.d/sige_master && \
    echo "  create 0644 root root" >> /etc/logrotate.d/sige_master && \
    echo "}" >> /etc/logrotate.d/sige_master


# ----------------------------------< cron >-----------------------------------------------
RUN wget https://cronitor.io/dl/linux_amd64.tar.gz \
    && tar xvf linux\_amd64.tar.gz -C /usr/local/bin/

COPY crons/cronjob /etc/cron.d/sige-cron
RUN chmod 0644 /etc/cron.d/sige-cron && \
    /usr/bin/crontab /etc/cron.d/sige-cron
    
CMD ["/sige-master/scripts/start.sh"]
