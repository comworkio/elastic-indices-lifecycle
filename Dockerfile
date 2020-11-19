FROM ubuntu:20.04

ENV PYTHONUNBUFFERED "1"
ENV PYTHONIOENCODING "UTF-8"

RUN apt-get update -y && \
    apt-get install curl telnet net-tools wget python3 python3-pip libcurl4-openssl-dev libssl-dev -y && \
    pip3 install elasticsearch pycurl

COPY rollup.py rollup_conf.json /

CMD [ "python3", "/rollup.py" ]
