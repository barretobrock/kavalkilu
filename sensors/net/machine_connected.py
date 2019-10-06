#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. When connections change, will post to channel"""
import pandas as pd
from kavalkilu import Log, LogArgParser, MySQLLocal, SlackTools, NetTools, Hosts


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('device_connected', log_lvl=LogArgParser().loglvl)

db_eng = MySQLLocal('logdb')

ip_addr = NetTools().get_ip()
machine_name = Hosts().get_host(ip=ip_addr)['name']

log.debug('Pinging device...')
# Ping phone's ip and check response
status = NetTools(host=machine_name).ping()
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
""".format(machine_name)
log.debug('Querying for last ping...')
last_ping = pd.read_sql_query(last_ping_query, con=db_eng.connection)

today = pd.datetime.now()
st = SlackTools()
if last_ping.empty:
    # Machine is not yet in database. Add it.
    log.info('New machine logged: {}'.format(machine_name))
    slack_msg = 'A new machine (`{}`) will be loaded into `logdb.devices`.'.format(machine_name)
    st.send_message('notifications', slack_msg)
    new_machine_dict = {
        'name': machine_name,
        'ip': ip_addr,
        'status': status,
        'update_date': today
    }
    db_eng.write_dataframe('devices', pd.DataFrame(new_machine_dict, index=[0]))
else:
    # Check if uptime matches the uptime in the db
    db_status = last_ping['status'].values[0]
    if db_status != status:
        # If not, update the uptime in the db
        log.debug('Status changed from {} to {} for device {}.'.format(db_status, status, machine_name))
        slack_msg = 'Machine `{}` changed connection status from {} to {}. Its new status will be' \
                    ' loaded into `logdb.devices`.'.format(machine_name, db_status, status)
        st.send_message('notifications', slack_msg)
        update_uptime_query = """
            UPDATE
                devices
            SET
                status = '{}'
                , update_date = NOW()
            WHERE
                name = '{}'
                AND ip = '{}'
        """.format(status, machine_name, ip_addr)
        db_eng.write_sql(update_uptime_query)

log.close()
