# ================================================================
# Dockerfile para DEV com mais ferramentas e imagem mais pesada
# ================================================================
FROM python:3.11.2-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    logrotate \
    cron \
    tzdata \
    postgresql-client \
    locales \
    iputils-ping \
    net-tools \
    dnsutils \
    curl \
    git \
    vi \
    nano \
    zsh \
    powerline \
    curl \
    wget


ARG API_KEY

RUN wget https://cronitor.io/dl/linux_amd64.tar.gz \
    && tar xvf linux\_amd64.tar.gz -C /usr/local/bin/ \
    && cronitor configure --api-key ${API_KEY}

WORKDIR /sige-master
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /sige-master

RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)" -- \
    -t https://github.com/romkatv/powerlevel10k \
    -p git \
    -p git-flow \
    -p https://github.com/zdharma-continuum/fast-syntax-highlighting \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions \
    -a 'export TERM=xterm-256color'


RUN echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> ~/.zshrc && \
    echo 'HISTFILE=/home/python/zsh/.zsh_history' >> ~/.zshrc 

# Setting cron
COPY crons/cronjob /etc/cron.d/sige-cron
RUN chmod 0644 /etc/cron.d/sige-cron && \
    /usr/bin/crontab /etc/cron.d/sige-cron

# Permissions for logs directory
RUN chmod -R 777 /sige-master/logs

CMD cron && tail -f /sige-master/logs/cron_output.log
