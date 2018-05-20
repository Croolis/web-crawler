FROM ubuntu:16.04

RUN mkdir /app
WORKDIR /app

RUN apt-get update \
    && apt-get install python-pip -y \
    && apt-get install python3-pip -y \
    && apt-get install python3-dev -y \
    && apt-get install wget -y

RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.20.1/geckodriver-v0.20.1-linux64.tar.gz \
    && tar -xvzf geckodriver* \
    && mv geckodriver /usr/bin/ \
    && chmod +x /usr/bin/geckodriver \
    && rm -rf geckodriver*

RUN pip install --disable-pip-version-check supervisor==3.3.1

COPY requirements.txt .
RUN pip3 install --disable-pip-version-check pip==9.0.3 \
    && pip3 install --disable-pip-version-check --no-cache-dir -r requirements.txt \
    && rm requirements.txt

COPY setup.py ./
COPY scheduler/ ./scheduler/
RUN pip3 install -e .

COPY /etc/worker.sh /usr/bin/runtiger
RUN chmod +x /usr/bin/runtiger

RUN mkdir -p /var/run/scheduler/ \
    && chown -R www-data: /var/run/scheduler/

ENTRYPOINT ["runtiger"]
