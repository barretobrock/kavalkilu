#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. When connections change, will post to channel"""
import pandas as pd
from kavalkilu import Log, LogArgParser, MySQLLocal, NetTools, Hosts
from slacktools import SlackTools


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('device_connected', log_lvl=LogArgParser().loglvl)

eng = MySQLLocal('logdb')

device = 'an-barret'
log.debug('Pinging device...')
# Ping phone's ip and check response
status = NetTools(host=device).ping()
log.debug('Ping result: {}'.format(status))

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

try:
    last_ping_status = last_ping['status'].values[0]
    new_device = False
except IndexError:
    # No info for this device yet.
    last_ping_status = status
    new_device = True

if last_ping_status != status or new_device:
    # Status has changed. Update the channel
    if new_device:
        msg = 'New device connected: `{}`'.format(device)
    elif last_ping_status == 'CONNECTED':
        # Phone disconnected
        msg = 'Mehe ühik on koduvõrgust läinud :sadcowblob:'
    else:
        msg = '<@UM3E3G72S> Mehe ühik on taas koduvõrgus! :meow_party:'
    log.debug("Sending message to Slack channel")
    SlackTools(log).send_message('wifi-pinger-dinger', msg)

if new_device:
    new_dev_dict = {
        'name': device,
        'ip': Hosts().get_host(name=device)['ip'],
        'status': status
    }
    log.info('Adding new device to table: {}.'.format(device))
    eng.write_dataframe('devices', pd.DataFrame(new_dev_dict, index=[0]))
else:
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
    log.debug('Updating table.')
    eng.write_sql(query)

log.close()
