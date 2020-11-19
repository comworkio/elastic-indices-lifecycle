FROM ubuntu:20.04

LABEL Description="Python docker service image"

ENV PYTHONUNBUFFERED "1"
ENV PYTHONIOENCODING "UTF-8"

RUN apt-get update -y && \
    apt-get install curl telnet net-tools wget python3 python3-pip libcurl4-openssl-dev libssl-dev -y && \
    pip3 install elasticsearch pycurl

CMD [ "python3", "/purge.py" ]
