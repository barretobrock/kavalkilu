#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Posts error logs to #errors channel in Slack"""
import pandas as pd
from kavalkilu import MySQLLocal, SlackBot


db = MySQLLocal('logdb')
mysqlconn = db.engine.connect()
sb = SlackBot()

# We read errors from x hours previous
# Currently, logs are read in every day at 6AM, so this will be 24 hours while we test it
hour_interval = 24
# The date to measure from
read_from = (pd.datetime.today() - pd.Timedelta(hours=hour_interval)).replace(minute=0, second=0)

error_logs_query = """
    SELECT 
        machine_name
        , log_name
        , time AS log_timestamp
        , level AS log_level
        , type AS log_type
    FROM 
        logs
    WHERE
        time >= '{:%F %T}'
    ORDER BY 
        time ASC 
    LIMIT 
        10
""".format(read_from)
result_df = pd.read_sql_query(error_logs_query, mysqlconn)

log_splitter = {
    'normal': {
        'channel': '#logs',
        'levels': ['DEBUG', 'INFO']
    },
    'errors': {
        'channel': '#errors',
        'levels': ['ERROR', 'WARN']
    }
}


if not result_df.empty:
    for log_type, log_dict in log_splitter.items():
        df = result_df[result_df.log_level.isin(log_dict['levels'])]
        if not df.empty:
            # Send the info to Slack
            msg = """*Today's log output*:\n\n```{}````""".format(df.to_string(index=False, show_dimensions=True))
            sb.send_message(log_dict['channel'], msg)


