FROM ubuntu:16.04

RUN mkdir /app
WORKDIR /app

RUN apt-get update \
    && apt-get install cron -y \
    && apt-get install redis-server -y \
    && apt-get install python-pip -y \
    && apt-get install python3-pip -y \
    && apt-get install python3-dev -y \
    && apt-get install curl -y \
    && apt-get install wget -y

RUN curl https://gist.githubusercontent.com/PreFX48/b40e22a9beb8ad17b6c7c1f989406dfb/raw/efb7b4b44135fb4bf0959b3a667bb81aa4dc2998/install_chrome_and_drivers.sh | bash

RUN pip install --disable-pip-version-check supervisor==3.3.1

COPY requirements.txt .
RUN pip3 install --disable-pip-version-check pip==9.0.3 \
    && pip3 install --disable-pip-version-check --no-cache-dir -r requirements.txt \
    && rm requirements.txt

COPY setup.py ./
COPY scheduler/ ./scheduler/
RUN pip3 install -e .

COPY etc/ /etc/

COPY /etc/taskrunner.py /usr/bin/taskrunner
RUN chmod +x /usr/bin/taskrunner

RUN mkdir -p /var/run/scheduler/ \
    && chown -R www-data: /var/run/scheduler/

RUN rm /etc/supervisord.conf.d/tasktiger.conf

EXPOSE 80 6379

ENTRYPOINT ["supervisord"]
