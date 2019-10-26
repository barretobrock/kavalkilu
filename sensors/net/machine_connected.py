#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. When connections change, will post to channel"""
import os
import pandas as pd
from kavalkilu import Log, LogArgParser, NetTools, Hosts, Paths
from slacktools import SlackTools


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('machine_conn', log_lvl=LogArgParser().loglvl)
today = pd.datetime.now()
st = SlackTools(log)

fpath = os.path.join(os.path.abspath(Paths().data_dir), 'machine_connected.json')

# Get connections of all the device we want to track
machines = Hosts().get_hosts(regex=r'^(lt|ac|an|pi|homeserv).*')
machines_df = pd.DataFrame(machines)

# Read in the json file if there is one
if os.path.exists(fpath):
    cur_state_df = pd.read_json(fpath)
else:
    cur_state_df = machines_df.copy()
    for col in ['status', 'update_date', 'connected_since']:
        cur_state_df[col] = None

cur_state_df = cur_state_df.rename(columns={'status': 'prev_status'})
# Merge with machines_df
machines_df = machines_df.merge(cur_state_df, how='left', on=['name', 'ip'])

for i, row in machines_df.iterrows():
    # Ping machine
    machine_name = row['name']
    prev_status = row['prev_status']
    status = NetTools(ip=row['ip']).ping()
    log.debug('Ping result for {}: {}'.format(machine_name, status))
    machines_df.loc[i, 'status'] = status
    if pd.isnull(prev_status):
        # Log new machine regardless of current status
        log.info('New machine logged: {}'.format(machine_name))
        slack_msg = 'A new machine `{}` will be loaded into `logdb.devices`.'.format(machine_name)
        st.send_message('notifications', slack_msg)
        machines_df.loc[i, 'update_date'] = today
        machines_df.loc[i, 'connected_since'] = today
    else:
        if status != prev_status:
            # State change
            log.info('Machine changed state: {}'.format(machine_name))
            slack_msg = '`{}` changed state from `{}` to `{}`. Record made in `logdb.devices`.'.format(
                machine_name, prev_status, status)
            st.send_message('notifications', slack_msg)
            machines_df.loc[i, 'update_date'] = today

# Notify on specific device state changes
for devname in ['an-barret']:
    df = machines_df.loc[machines_df.name == devname]
    prev_status = df['prev_status'].values[0]
    status = df['status'].values[0]
    if not pd.isnull(prev_status):
        if prev_status != status:
            if status == 'CONNECTED':
                msg = '<@UM3E3G72S> Mehe ühik on taas koduvõrgus! :meow_party:'
            else:
                msg = 'Mehe ühik on koduvõrgust läinud :sadcowblob:'
            st.send_message('wifi-pinger-dinger', msg)


# Enforce column order
machines_df = machines_df[['name', 'ip', 'status', 'update_date', 'connected_since']]

# Save to JSON
machines_df.to_json(fpath)

log.close()
