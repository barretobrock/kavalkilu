#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Posts error logs to #errors channel in Slack"""
import pandas as pd
from kavalkilu import MySQLLocal, SlackTools


db = MySQLLocal('logdb')
mysqlconn = db.engine.connect()
st = SlackTools()

# We read errors from x hours previous
# Currently, logs are read in every day at 6AM, so this will be 24 hours while we test it
hour_interval = 4
# The date to measure from
read_from = (pd.datetime.today() - pd.Timedelta(hours=hour_interval)).replace(minute=0, second=0)

error_logs_query = """
    SELECT 
        machine_name AS machine
        , log_name AS log
        , time AS log_ts
        , level AS lvl
    FROM 
        logs
    WHERE
        time >= '{:%F %T}'
    ORDER BY 
        time ASC 
""".format(read_from)
result_df = pd.read_sql_query(error_logs_query, mysqlconn)
result_df['cnt'] = 1
result_df = result_df.groupby(['machine', 'log', 'lvl',
                               pd.Grouper(key='log_ts', freq='D')]).count().reset_index()


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

if not result_df.empty:
    for log_type, log_dict in log_splitter.items():
        df = result_df[result_df.lvl.isin(log_dict['levels'])].copy()
        df['lvl'] = df['lvl'].str[:3]
        df['log'] = df['log'].str[:10]
        df['log_ts'] = pd.to_datetime(df['log_ts']).dt.strftime('%d %b')
        df.loc['total'] = df.copy().sum(numeric_only=True)
        df['cnt'] = df['cnt'].astype(int)
        df = df.fillna('')
        channel = log_dict['channel']
        if not df.empty:
            # Send the info to Slack
            msg = """*Last 24 hours in {}*:\n\n```{}````""".format(channel, sb.st.df_to_slack_table(df))
        else:
            msg = 'No {} logs for this round.'.format(log_type)
        st.send_message(channel, msg)
else:
    channel = '#logs'
    msg = 'No logs were able to be captured in either category.'
    st.send_message(channel, msg)



