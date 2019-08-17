#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. When connections change, will post to channel"""
import pandas as pd
from kavalkilu import Log, MySQLLocal, SlackBot, NetTools


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('device_connected', log_lvl='DEBUG')
log.debug('Logging initiated')

# conn = MySQLLocal('logdb').engine.connect()
eng = MySQLLocal('logdb')

device = 'an_barret'
log.debug('Pinging device...')
# Ping phone's ip and check response
status = NetTools(host=device).ping()

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
log.debug('Querying for last ping...')
last_ping = pd.read_sql_query(last_ping_query, con=eng.connection)

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
# Update values in table
eng.write_sql(query)

log.close()
