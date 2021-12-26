FROM ubuntu:20.04 AS base

ENV PYTHONUNBUFFERED "1"
ENV PYTHONIOENCODING "UTF-8"

COPY requirements.txt /

RUN apt-get update -y && \
    apt-get install curl libcurl4-openssl-dev libssl-dev python3 python3-pip -y && \
    pip3 install -r /requirements.txt

CMD [ "python3", "/script.py" ]

FROM base AS rollup

COPY rollup/rollup.py  /script.py
COPY rollup/rollup_conf.json /

FROM base AS backup

COPY backup/backup.py /script.py
COPY backup/backup_config.json /
