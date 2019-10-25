#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. When connections change, will post to channel"""
import pandas as pd
from kavalkilu import Log, LogArgParser, MySQLLocal, NetTools, Hosts
from slacktools import SlackTools


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('machine_conn', log_lvl=LogArgParser().loglvl)
today = pd.datetime.now()
st = SlackTools(log)
db_eng = MySQLLocal('logdb')

# Get connections of all the device we want to track
machines = Hosts().get_hosts(regex=r'^(lt|ac|an|pi|homeserv).*')
machines_df = pd.DataFrame(machines)

# Collect current state of these machines
cur_state_query = """
SELECT
    *
FROM
    devices AS d 
WHERE
    d.ip IN {}
""".format(tuple(machines_df.ip.unique().tolist()))
cur_state = pd.read_sql_query(cur_state_query, db_eng.connection)
cur_state = cur_state.rename(columns={'status': 'prev_status'})
# Merge with machines_df
machines_df = machines_df.merge(cur_state, how='left', on=['name', 'ip'])

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
    if prev_status != status:
        if df['status'] == 'CONNECTED':
            msg = '<@UM3E3G72S> Mehe ühik on taas koduvõrgus! :meow_party:'
        else:
            msg = 'Mehe ühik on koduvõrgust läinud :sadcowblob:'
        st.send_message('wifi-pinger-dinger', msg)


# Enforce column order
machines_df = machines_df[['name', 'ip', 'status', 'update_date', 'uptime_since']]

# Update database
machines_df.to_sql('devices', db_eng.connection, if_exists='replace', index_label='id')

log.close()
