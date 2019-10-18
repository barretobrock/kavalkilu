#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Posts error logs to #errors channel in Slack"""
import pandas as pd
from kavalkilu import MySQLLocal, Log, LogArgParser
from slacktools import SlackTools


log = Log('slack_logger', log_lvl=LogArgParser().loglvl)
db = MySQLLocal('logdb')
mysqlconn = db.engine.connect()
st = SlackTools(log)

log_splitter = {
    'normal': {
        'channel': '#logs',
        'levels': ['DEBUG', 'INFO']
    },
    'error': {
        'channel': '#errors',
        'levels': ['ERROR', 'WARN']
    }
}

# We read errors from x hours previous
hour_interval = 4
now = pd.datetime.now()
# The date to measure from
read_from = (now - pd.Timedelta(hours=hour_interval)).replace(minute=0, second=0)

error_logs_query = """
    SELECT 
        machine_name AS machine
        , log_name AS log
        , time AS log_ts
        , level AS lvl
        , exc_class
        , exc_msg
    FROM 
        logs
    WHERE
        time >= '{:%F %T}'
    ORDER BY 
        time ASC 
""".format(read_from)
result_df = pd.read_sql_query(error_logs_query, mysqlconn)
if not result_df.empty:
    result_df['cnt'] = 1
    result_df = result_df.groupby(['machine', 'log', 'lvl', 'exc_class', 'exc_msg',
                                   pd.Grouper(key='log_ts', freq='H')]).count().reset_index()
    # Establish column order
    result_df = result_df[['log_ts', 'machine', 'log', 'lvl', 'exc_class', 'exc_msg', 'cnt']]
    for log_type, log_dict in log_splitter.items():
        channel = log_dict['channel']
        df = result_df[result_df.lvl.isin(log_dict['levels'])].copy()
        if df.shape[0] > 0:
            df['log_ts'] = pd.to_datetime(df['log_ts']).dt.strftime('%d %b %H:%M')
            df.loc['total'] = df.copy().sum(numeric_only=True)
            df['cnt'] = df['cnt'].astype(int)
            df = df.fillna('')
            if log_type == 'normal':
                # remove the exception-related columns
                df = df.drop(['exc_class', 'exc_msg'], axis=1)
            # Send the info to Slack
            msg = """`{:%H:%M}` to `{:%H:%M}` in `{}`:\n\n```{}```""".format(read_from, now,
                                                                             channel, st.df_to_slack_table(df))
        else:
            msg = 'No {} logs for the period `{:%H:%M}` to `{:%H:%M}`.'.format(log_type, read_from, now)
        st.send_message(channel, msg)
else:
    channel = '#logs'
    msg = 'No logs were able to be captured in either category ' \
          'for the period `{:%H:%M}` to `{:%H:%M}`'.format(read_from, now)
    st.send_message(channel, msg)



