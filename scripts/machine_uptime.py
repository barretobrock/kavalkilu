#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""For given machine, collects when device was last booted up"""
import time
import psutil
import pandas as pd
from kavalkilu import Log, LogArgParser, MySQLLocal, Hosts, DateTools, NetTools
from kavalkilu.local_tools import slack_comm, alert_channel


log = Log('machine_uptime', log_lvl=LogArgParser().loglvl)

ip_addr = NetTools().ip
machine_name = Hosts().get_host(ip=ip_addr)['name']

dt = DateTools()
uptime = dt.unix_to_string(psutil.boot_time(), '%F %T')
today = pd.datetime.now().strftime('%F %T')

db_eng = MySQLLocal('logdb')
# Find the boot time in the database
uptime_query = """
SELECT
    d.name
    , d.uptime_since AS uptime_ts
    , d.update_date AS update_ts
FROM
    devices AS d 
WHERE
    d.name = '{}'
    AND d.ip = '{}'
""".format(machine_name, ip_addr)
uptime_df = pd.read_sql_query(uptime_query, db_eng.connection)

if uptime_df.empty:
    # Machine is not yet in database. Add it.
    log.info(f'New machine logged: {machine_name}')
    slack_msg = f'A new machine (`{machine_name}`) will be loaded into `logdb.devices`.'
    slack_comm.send_message(alert_channel, slack_msg)
    new_machine_dict = {
        'name': machine_name,
        'ip': ip_addr,
        'status': 'CONNECTED',
        'update_date': today,
        'uptime_since': uptime
    }
    db_eng.write_dataframe('devices', pd.DataFrame(new_machine_dict, index=[0]))
else:
    # Check if uptime matches the uptime in the db
    db_uptime = uptime_df['uptime_ts'].dt.strftime('%F %T').values[0]
    if db_uptime != uptime:
        # If not, update the uptime in the db
        log.debug(f'Uptime measured ({uptime}) did not match uptime in db ({db_uptime}). Updating db.')
        slack_msg = f'Machine `{machine_name}` was recently rebooted. Its new uptime of `{uptime}` will be' \
                    ' loaded into `logdb.devices`.'
        update_uptime_query = """
            UPDATE
                devices
            SET
                uptime_since = TIMESTAMP('{}')
                , update_date = NOW()
            WHERE
                name = '{}'
                AND ip = '{}'
        """.format(uptime, machine_name, ip_addr)
        db_eng.write_sql(update_uptime_query)
        time.sleep(2)
        slack_comm.send_message(alert_channel, slack_msg)

log.close()
