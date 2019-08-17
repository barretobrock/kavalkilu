#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. When connections change, will post to channel"""
import subprocess
import pandas as pd
from kavalkilu import Log, Hosts, MySQLLocal, SlackBot


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('device_connected', log_lvl='DEBUG')
log.debug('Logging initiated')

conn = MySQLLocal('logdb').engine.connect()
# Establish transaction
trans = conn.begin()

device = 'an_barret'
phone = Hosts().get_host(device)['ip']
# Ping phone's ip and check response
proc = subprocess.Popen(
    ['ping', '-c', '2', phone],
    stdout=subprocess.PIPE
)
stdout, stderr = proc.communicate()

# pull last_ping for device from db here
last_ping_query = """
SELECT
    d.name
    , d.status AS status
    , d.update_date AS update_ts
FROM
    devices AS d 
WHERE
    d.name = '{}'
""".format(device)
last_ping = pd.read_sql_query(last_ping_query, con=conn)
# if last ping was greater than 5 mins, change status

if proc.returncode == 0:
    # Successfully pinged phone
    status = 'CONNECTED'
else:
    status = 'DISCONNECTED'

last_ping_status = last_ping['status'].values[0]
if last_ping_status != status:
    # Status has changed. Update the channel
    if last_ping_status == 'CONNECTED':
        # Phone disconnected
        msg = 'Mehe ühik on koduvõrgust läinud :sadcowblob:'
    else:
        msg = '<@UM3E3G72S> Mehe ühik on taas koduvõrgus! :meow_party:'
    sb = SlackBot().send_message('wifi-pinger-dinger', msg)

query = """
    UPDATE
        devices
    SET
        status = '{}'
        , update_date = NOW()
    WHERE
        name = '{}'
""".format(status, device)
try:
    r = conn.execute(query)
    trans.commit()
except:
    trans.rollback()

conn.close()

log.close()
