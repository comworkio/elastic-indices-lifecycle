import json

from time import sleep
from elasticsearch import Elasticsearch
from datetime import datetime
import pycurl
import re
import os

def override_conf_from_env( conf, key ):
    env_key = "ES_LIFECYCLE_{}".format(key)
    if os.environ.get(env_key) is not None:
        conf[key] = os.environ[env_key]

def override_conf_from_env_array( conf, key ):
    env_key = "ES_LIFECYCLE_{}".format(key)
    if os.environ.get(env_key) is not None:
        if os.environ[env_key] is None or os.environ[env_key] == "" or os.environ[env_key] == "null":
            conf[key] = []
        else:
            conf[key] = os.environ[env_key].split(",")

conf=[]
with open('rollup_conf.json') as json_file:
    conf = json.load(json_file)

override_conf_from_env(conf, 'elastic_hosts')
override_conf_from_env(conf, 'elastic_port')
override_conf_from_env(conf, 'elastic_scheme')
override_conf_from_env(conf, 'wait_time')
override_conf_from_env(conf, 'retention')
override_conf_from_env(conf, 'elastic_username')
override_conf_from_env(conf, 'elastic_password')
override_conf_from_env(conf, 'should_slack')
override_conf_from_env(conf, 'slack_token')
override_conf_from_env(conf, 'slack_username')
override_conf_from_env(conf, 'slack_channel')
override_conf_from_env(conf, 'slack_emoji')
override_conf_from_env(conf, 'log_level')
override_conf_from_env(conf, 'date_format')
override_conf_from_env_array(conf, 'index_prefixes')
override_conf_from_env_array(conf, 'index_suffixes')

ES_HOSTS = conf['elastic_hosts']
ES_PORT = int(conf['elastic_port'])
ES_SCHEME = conf['elastic_scheme']
WAIT_TIME = int(conf['wait_time'])
INDEX_PREFIXES = conf['index_prefixes']
INDEX_SUFFIXES = conf['index_suffixes']
RETENTION = int(conf['retention'])
ES_USER = conf['elastic_username']
ES_PASS = conf['elastic_password']
SLACK_TRIGGER = conf['should_slack']
SLACK_URL = "https://hooks.slack.com/services/{}".format(conf['slack_token'])
SLACK_USERNAME = conf['slack_username']
SLACK_CHANNEL = conf['slack_channel']
SLACK_EMOJI = conf['slack_emoji']
LOG_LEVEL = conf['log_level']
DATE_FORMAT = conf['date_format']

es = Elasticsearch(ES_HOSTS, http_auth=(ES_USER, ES_PASS), scheme = ES_SCHEME, port = ES_PORT)

def slack_message( message ):
    if SLACK_TRIGGER == 'on':
        c = pycurl.Curl()
        c.setopt(pycurl.URL, SLACK_URL)
        c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        c.setopt(pycurl.POST, 1)
        data = json.dumps({"text": message, "username": SLACK_USERNAME, "channel": SLACK_CHANNEL, "icon_emoji": SLACK_EMOJI })
        c.setopt(pycurl.POSTFIELDS, data)
        c.perform()

def check_log_level ( log_level ):
    if LOG_LEVEL == "debug" or LOG_LEVEL == "DEBUG":
        return True
    else:
        return log_level != "debug" and log_level != "DEBUG"

def quiet_log_msg ( log_level, message ):
    if check_log_level(log_level):
        print ("[{}] {}".format(log_level, message))

def log_msg( log_level, message ):
    if check_log_level(log_level):
        quiet_log_msg (log_level, message)
        slack_message(message)

def perform_delete( indice, creation_date ):
    d = (datetime.now() - creation_date).days
    quiet_log_msg("debug", "Check if d={} >= r={} for the indice {}".format(d, RETENTION, indice))
    if d >= RETENTION:
        log_msg("info", "Removing indice i={} because d={} >= r={}".format(indice, d, RETENTION))
        es.indices.delete(index=indice, ignore=[400, 404])

while True:
    log_msg("debug", "Configuration : log_level = {}, should_slack = {}, elastic_hosts = {}, elastic_user = {}, date_format = {}".format(LOG_LEVEL, SLACK_TRIGGER, ES_HOSTS, ES_USER, DATE_FORMAT))
    log_msg("info", "Check if indices matching with prefixes = {} and suffixes = {}".format(INDEX_PREFIXES, INDEX_SUFFIXES))
    for indice in es.indices.get('*'):
        quiet_log_msg("debug", "Check if indice {} match with prefixes or suffixes".format(indice))

        if INDEX_PREFIXES:
            for prefix in INDEX_PREFIXES:
                if indice.startswith(prefix):
                    creation_date =  datetime.strptime(indice, "{}-{}".format(prefix, DATE_FORMAT))
                    quiet_log_msg("debug", "Check indice {} with creation_date : {} because of prefix {}".format(indice, creation_date, prefix))
                    perform_delete(indice, creation_date)

        if INDEX_SUFFIXES:
            for suffix in INDEX_SUFFIXES:
                capture = re.findall("^.*{}-([0-9\-]+)$".format(suffix), indice)
                if capture:
                    creation_date =  datetime.strptime(capture[0], DATE_FORMAT)
                    quiet_log_msg("debug", "Check indice {} with creation_date : {} because of suffix {}".format(indice, creation_date, suffix))
                    perform_delete(indice, creation_date)
    sleep(WAIT_TIME)
