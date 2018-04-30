FROM ubuntu:16.04

RUN mkdir /app
WORKDIR /app

RUN apt-get update \
    && apt-get install python-pip -y \
    && apt-get install python3-pip -y \
    && apt-get install python3-dev -y

RUN pip install --disable-pip-version-check supervisor==3.3.1

COPY requirements.txt .
RUN pip3 install --disable-pip-version-check pip==9.0.3 \
    && pip3 install --disable-pip-version-check --no-cache-dir -r requirements.txt \
    && rm requirements.txt

COPY setup.py ./
COPY scheduler/ ./scheduler/
RUN pip3 install -e .

COPY etc/ /etc/

RUN rm /etc/supervisord.conf.d/scheduler.conf \
    && rm /etc/supervisord.conf.d/redis.conf

ENTRYPOINT ["supervisord"]
