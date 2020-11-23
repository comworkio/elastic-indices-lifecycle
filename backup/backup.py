import time
import datetime
import pycurl
import json
import os
import sys
import pwd
from base64 import b64encode
from time import sleep
from io import BytesIO

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

conf={}
with open('backup_config.json') as json_file:
    conf = json.load(json_file)

override_conf_from_env(conf, 'hostname')
override_conf_from_env(conf, 'slack_token')
override_conf_from_env(conf, 'elastic_scheme')
override_conf_from_env(conf, 'elastic_config_url')
override_conf_from_env(conf, 'retention')
override_conf_from_env(conf, 'elastic_username')
override_conf_from_env(conf, 'elastic_backup_repository')
override_conf_from_env(conf, 'should_slack')
override_conf_from_env(conf, 'slack_token')
override_conf_from_env(conf, 'slack_username')
override_conf_from_env(conf, 'slack_channel')
override_conf_from_env(conf, 'slack_emoji')
override_conf_from_env(conf, 'elastic_backup_path')
override_conf_from_env(conf, 'elastic_backup_retention')
override_conf_from_env(conf, 'elastic_username')
override_conf_from_env(conf, 'elastic_password')
override_conf_from_env(conf, 'log_level')
override_conf_from_env(conf, 'fs_user')
override_conf_from_env(conf, 'fs_group')
override_conf_from_env(conf, 'wait_time')

hostname = conf['hostname']
slack_url = "https://hooks.slack.com/services/{}".format(conf['slack_token'])
elastic_config_url = "{}/_snapshot/{}".format(conf['elastic_config_url'], conf['elastic_backup_repository'])
slack_trigger = conf['should_slack']
slack_username = conf['slack_username']
slack_channel = conf['slack_channel']
slack_emoji = conf['slack_emoji']
elastic_backup_path = conf['elastic_backup_path']
elastic_backup_retention = conf['elastic_backup_retention']
elastic_username = conf['elastic_username']
elastic_password = conf['elastic_password']
log_level = conf['log_level']
pycurl_verbose = False

if log_level == "debug":
    pycurl_verbose = True

fs_user = conf['fs_user']
fs_group = conf['fs_group']
wait_time = conf['wait_time']
user_password = "{}:{}".format(elastic_username, elastic_password)
user_password_encoded = b64encode(user_password.encode()).decode("ascii")
http_auth_header = "Authorization: Basic {}".format(user_password_encoded)
http_headers = ['Accept: application/json', 'Content-Type: application/json', http_auth_header];

def slack_message( message ):
    if slack_trigger == 'on':
        c = pycurl.Curl()
        c.setopt(pycurl.URL, slack_url)
        c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        c.setopt(pycurl.POST, 1)
        data = json.dumps({"text": message, "username": slack_username, "channel": slack_channel, "icon_emoji": slack_emoji })
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

def quiet_mkdir( dirName ):
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        quiet_log_msg("debug", "[quiet_mkdir] Directory {} created".format(dirName))
    else:
        quiet_log_msg("debug", "[quiet_mkdir] Directory {} already exists".format(dirName))
    uid, gid =  pwd.getpwnam(fs_user).pw_uid, pwd.getpwnam(fs_group).pw_uid
    os.chown(dirName, uid, gid)
    quiet_log_msg("debug", "[quiet_mkdir] chown {} with user = {}, group = {}, uid = {}, gid = {}".format(dirName, fs_user, fs_group, uid, gid))

def check_snapshots_config( url, path ):
    if not os.path.exists(path):
        log_msg("info", "[{}][check_snapshots_config] | ElasticSearch | !!! ERROR !!! | Backup folder [{}] does not exists ...".format(hostname, path))
        sys.exit(1)
    full_path = "{}/{}".format(path, hostname)
    quiet_mkdir(full_path)
    log_msg("info", "[{}][check_snapshots_config] | ElasticSearch | Creating repository config on elastic: {}".format(hostname, full_path))
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, http_headers)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.VERBOSE, pycurl_verbose)
    data = json.dumps({"type":"fs", "settings":{"location": full_path, "compress": True}})
    c.setopt(pycurl.POSTFIELDS, data)
    c.perform()
    rtn_code = c.getinfo(pycurl.RESPONSE_CODE)
    log_msg("info", "[{}][check_snapshots_config] | ElasticSearch | Repository config [{}] generated successfully... (code = {})".format(hostname, url, rtn_code))

def elastic_snapshot( st ):
    url = elastic_config_url + '/' + hostname + '-' + str(st) + '?wait_for_completion=true&pretty'
    log_msg("info", "[{}][elastic_snapshot] | ElasticSearch | Creating snapshot on elastic: {}".format(hostname, url))
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, http_headers)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.VERBOSE, pycurl_verbose)
    data = ''
    c.setopt(pycurl.POSTFIELDS, data)
    c.perform()
    rtn_code = c.getinfo(pycurl.RESPONSE_CODE)
    log_msg("info", "[{}][elastic_snapshot] | ElasticSearch | Snapshot [{}-{}] generated successfully... (code = {})".format(hostname, hostname, str(st), rtn_code))

def delete_snapshot( snapshot ):
    log_msg("info", "[{}][delete_snapshot] | ElasticSearch | Delete snapshot on filesystem: {}".format(hostname, snapshot))
    c = pycurl.Curl()
    c.setopt(pycurl.URL, elastic_config_url + '/' + snapshot)
    c.setopt(pycurl.HTTPHEADER, http_headers)
    c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
    c.setopt(pycurl.VERBOSE, pycurl_verbose)
    data = ''
    c.setopt(pycurl.POSTFIELDS, data)
    c.perform()
    rtn_code = c.getinfo(pycurl.RESPONSE_CODE)
    log_msg ("info", "[{}][delete_snapshot] | ElasticSearch | Snapshot [{}] deleted successfully... (code = {})".format(hostname, snapshot, rtn_code))

def get_snapshot_name_from_uuid ( uuid ):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, elastic_config_url + '/_all')
    c.setopt(pycurl.HTTPHEADER, http_headers)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(pycurl.CUSTOMREQUEST, 'GET')
    c.setopt(pycurl.VERBOSE, pycurl_verbose)
    c.perform()
    json_body = buffer.getvalue().decode('UTF-8')
    snapshots = json.loads(json_body)
    for snapshot in snapshots['snapshots']:
        if snapshot['uuid'] == uuid:
            name = snapshot['snapshot']
            log_msg("info", "[{}][[get_snapshot_name_from_uuid] snapshot name for uuid = {} is {}".format(hostname, uuid, name))
            return name

    quiet_log_msg("debug", "[{}][get_snapshot_name_from_uuid] no name found for uuid = {}".format(hostname, uuid))
    return ""

def purge_elastic_backups( path, ts ):
    full_path = "{}/{}".format(path, hostname)
    for f in os.listdir(full_path):
        if f.startswith("snap-"):
            if os.stat(os.path.join(full_path, f)).st_mtime < ts - elastic_backup_retention * 86400:
                snapshot_raw = f
                snapshot_cleaned = snapshot_raw[5:]
                uuid = snapshot_cleaned[:-4]
                snapshot = get_snapshot_name_from_uuid(uuid)
                if snapshot != "":
                    delete_snapshot(snapshot)

while True:
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S')
    check_snapshots_config(elastic_config_url, elastic_backup_path)
    elastic_snapshot(st)
    purge_elastic_backups(elastic_backup_path, ts)
    sleep(wait_time)
