import json

from time import sleep
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionTimeout
from datetime import datetime
import pycurl
import re
import os
import sys

def is_not_empty ( var ):
    return var is not None and "" != var and "null" != var and "nil" != var

def is_empty ( var ):
    return not is_not_empty(var)

def override_conf_from_env( conf, key ):
    env_key = "ES_LIFECYCLE_{}".format(key)
    if os.environ.get(env_key) is not None:
        conf[key] = os.environ[env_key]
    elif not key in conf:
        conf[key] = "nil"

def override_conf_from_env_array( conf, key ):
    env_key = "ES_LIFECYCLE_{}".format(key)
    if os.environ.get(env_key) is not None:
        if is_empty(os.environ[env_key]):
            conf[key] = []
        else:
            conf[key] = os.environ[env_key].split(",")

conf={}
with open('rollup_conf.json') as json_file:
    conf = json.load(json_file)

override_conf_from_env(conf, 'elastic_subpath')
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
override_conf_from_env(conf, 'date_separator')
override_conf_from_env_array(conf, 'elastic_hosts')
override_conf_from_env_array(conf, 'index_prefixes')
override_conf_from_env_array(conf, 'index_suffixes')

ES_HOSTS = conf['elastic_hosts']
ES_SUBPATH = conf['elastic_subpath']
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
DATE_SEPARATOR = conf['date_separator']

if is_empty(DATE_SEPARATOR):
    DATE_SEPARATOR = '-'

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

if is_not_empty(ES_USER) and is_not_empty(ES_PASS) and is_not_empty(ES_SUBPATH):
    es_url_tpl = "{}://{}:{}@{}:{}/{}"
    es_url = es_url_tpl.format(ES_SCHEME, ES_USER, "{}", ES_HOSTS[0], ES_PORT, ES_SUBPATH)
    quiet_log_msg("debug", "Connect to elastic search with url = {}".format(es_url.format("XXXXXX")))
    es = Elasticsearch([es_url.format(ES_PASS)], http_auth=(ES_USER, ES_PASS))
elif is_not_empty(ES_USER) and is_not_empty(ES_PASS):
    es_url_tpl = "{}://{}:{}"
    es_url = es_url_tpl.format(ES_SCHEME, ES_HOSTS[0], ES_PORT)
    quiet_log_msg("debug", "Connect to elastic search with url = {} and username = {}".format(es_url, ES_USER))
    es = Elasticsearch(ES_HOSTS, http_auth=(ES_USER, ES_PASS), scheme = ES_SCHEME, port = ES_PORT)
elif is_not_empty(ES_SUBPATH):
    es_url_tpl = "{}://{}:{}/{}"
    es_url = es_url_tpl.format(ES_SCHEME, ES_HOSTS[0], ES_PORT, ES_SUBPATH)
    quiet_log_msg("debug", "Connect to elastic search with url = {}".format(es_url))
    es = Elasticsearch([es_url])
else:
    es_url_tpl = "{}://{}:{}"
    es_url = es_url_tpl.format(ES_SCHEME, ES_HOSTS[0], ES_PORT)
    quiet_log_msg("debug", "Connect to elastic search with url = {}".format(es_url))
    es = Elasticsearch(ES_HOSTS, scheme = ES_SCHEME, port = ES_PORT)

def perform_delete( indice, creation_date ):
    d = (datetime.now() - creation_date).days
    quiet_log_msg("debug", "Check if d={} >= r={} for the indice {}".format(d, RETENTION, indice))
    if d >= RETENTION:
        log_msg("info", "Removing indice i={} because d={} >= r={}".format(indice, d, RETENTION))
        try:
            es.indices.delete(index=indice, ignore=[400, 404])
        except:
            log_msg("error", "Unexpected error on deleting indice = {}, error = {}".format(indice, sys.exc_info()[0]))


while True:
    log_msg("debug", "Configuration : log_level = {}, should_slack = {}, elastic_hosts = {}, elastic_user = {}, date_format = {}".format(LOG_LEVEL, SLACK_TRIGGER, ES_HOSTS, ES_USER, DATE_FORMAT))
    log_msg("info", "Check if indices matching with prefixes = {} and suffixes = {}".format(INDEX_PREFIXES, INDEX_SUFFIXES))
    try:
        for indice in es.indices.get(index = '*'):
            quiet_log_msg("debug", "Check if indice {} match with prefixes or suffixes".format(indice))

            if INDEX_PREFIXES:
                quiet_log_msg("debug", "Check if indice i={} match with prefixes p=".format(indice, INDEX_PREFIXES))
                for prefix in INDEX_PREFIXES:
                    if indice.startswith(prefix):
                        try:
                            creation_date =  datetime.strptime(indice, "{}{}{}".format(prefix, DATE_SEPARATOR, DATE_FORMAT))
                            quiet_log_msg("debug", "Check indice {} with creation_date : {} because of prefix {}".format(indice, creation_date, prefix))
                            perform_delete(indice, creation_date)
                        except ValueError as ve:
                            log_msg("warn", "Unexpected ValueError = {} on indice = {}, skipping...".format(ve, indice))

            if INDEX_SUFFIXES:
                quiet_log_msg("debug", "Check if indice i={} match with suffixes s=".format(indice, INDEX_SUFFIXES))
                for suffix in INDEX_SUFFIXES:
                    capture = re.findall("^.*{}{}([0-9\-\.]+)$".format(suffix, DATE_SEPARATOR), indice)
                    if capture:
                        try:
                            creation_date =  datetime.strptime(capture[0], DATE_FORMAT)
                            quiet_log_msg("debug", "Check indice i={} with creation_date : {} because of suffix {}".format(indice, creation_date, suffix))
                            perform_delete(indice, creation_date)
                        except ValueError as ve:
                            log_msg("warn", "Unexpected ValueError = {} on indice = {}, skipping...".format(ve, indice))
    except ConnectionTimeout as cte:
        log_msg("error", "Unexpected ConnectionTimeout on indices loop = {}".format(cte))
    except:
        log_msg("error", "Unexpected error on indices loop = {}".format(sys.exc_info()[0]))
    sleep(WAIT_TIME)
