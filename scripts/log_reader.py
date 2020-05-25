#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Goes through log files for the given period and prepares them for import into a monitoring database"""
import os
import re
import pandas as pd
from kavalkilu import Paths, Log, LogArgParser, MySQLLocal, NetTools, Hosts


# Initiate logging (META!)
log = Log('log_collector', log_lvl=LogArgParser().loglvl)


def read_log_file(log_path, log_dict, most_recent_ts):
    """
    Determine which log parsing method to use and build out a mapping of the log
    Args:
        log_path: str, path to the log file
        log_dict: dict, contains mainly regex patterns to check against log entries
        most_recent_ts: pd.Timestamp, used to avoid picking logs that were likely already recorded

    Returns: pd.DataFrame
    """
    output_list = []
    with open(log_path, 'r') as file:
        # Set empty log type before we try to determine it
        lines = file.readlines()

    if len(lines) == 0:
        return pd.DataFrame(output_list)

    for k in log_dict.keys():
        if log_dict[k]['compiled'].search(lines[0]) is not None:
            # Use these predetermined patterns to parse through the log
            log_patterns = log_dict[k]
            break

    # Begin log parsing
    for i in range(0, len(lines)):
        line = lines[i]
        match = log_patterns['compiled'].match(line)
        if match is not None:
            match_str = match.group(0)
            match_list = match_str.split(' - ')

            log_ts = match_list[0]
            if log_ts > most_recent_ts.strftime('%F %T'):
                # Prepare log entry for entry into dataframe
                # Clean log name from time stamp at end
                log_name = match_list[1]
                if re.match(r'\d{4}', log_name.split('_')[-1]):
                    # Timestamp in log name. remove it
                    log_name = log_name[:-5]
                log_level = match_list[2].split(' ')[0]
                exc_class = ''
                exc_msg = ''
                if log_level in ['ERROR']:
                    # Grab more info (err class & message)
                    for j in range(i, len(lines) - 1):
                        # Try and find the error class
                        new_line = lines[j]
                        method1 = re.search(r'^\w+\:.*', new_line)
                        method2 = re.search(r'(Unexpected (\w|\s)+\:)((\w|\s)+\:)(.*)', new_line)

                        if method1 is not None:
                            # We've detected a line matching this: {exception}: {message}
                            exception = new_line.split(':')
                            exc_class = exception[0].strip()
                            exc_msg = exception[1].strip()
                            # Let iterator continue onward
                            i = j
                            break
                        elif method2 is not None:
                            # This is an already-caught exception
                            exc_class = method2.group(3).strip().replace(':', '')
                            exc_msg = method2.group(5).strip()
                            i = j
                            break
                        elif re.search(r'^\d+\-\d+\-\d+', new_line) is not None and j != i:
                            # We've gotten to a new item in the log. Call off the search for this mysterious class
                            exc_class = 'UnkException'
                            exc_msg = "Parsing pattern in log_reader couldn't find the Exception message"
                            i = j - 1
                            break

                output_list.append({
                    'time': log_ts,
                    'name': log_name,
                    'level': log_level,
                    'exc_class': exc_class,
                    'exc_msg': exc_msg,
                    'type': log_patterns['type']
                })

    return pd.DataFrame(output_list)


p = Paths()
log_dir = p.log_dir
machine_name = Hosts().get_host(ip=NetTools().ip)['name']

handler_dict = {
    'py_log': {
        'type': 'py',
        'regex': r'^\d+\-\d+\-\d+\s\d+\:\d+\:\d+\,\d+\s\-\s.*'
    },
    'sh_log': {
        'type': 'sh',
        'regex': r'^\d+\-\d+\-\d+\s\d+\:\d+\:\d+\s\-\s.*'
    }
}

# Include the compiler
for k, v in handler_dict.items():
    handler_dict[k]['compiled'] = re.compile(v['regex'])

# Establish connection with database
db = MySQLLocal('logdb')
mysqlconn = db.engine.connect()

# Query the logdb and find the most recent log entry for this machine
most_recent_query = """
    SELECT time
    FROM logs
    WHERE machine_name = '{}'
    ORDER BY time DESC 
    LIMIT 1
"""
most_recent = pd.read_sql_query(most_recent_query.format(machine_name), mysqlconn)
if most_recent.empty:
    # If no data, get log data for 10 days back
    most_recent_ts = (pd.datetime.now().replace(hour=0, minute=0, second=0) - pd.Timedelta('10 days'))
else:
    most_recent_ts = most_recent['time'].iloc[0]

log_df = pd.DataFrame()
for path, subdirs, files in os.walk(log_dir):
    for name in files:
        file_path = os.path.join(path, name)
        # Extract date string from log filename
        date_str = name[-12:-4]
        if date_str >= most_recent_ts.strftime('%Y%m%d'):
            # Continue with parsing current file
            log_item_df = read_log_file(file_path, handler_dict, most_recent_ts)
            if not log_item_df.empty:
                log_df = log_df.append(log_item_df)

if not log_df.empty:
    # Begin process to record to database
    # Establish order of log data
    log_df['machine_name'] = machine_name
    log_df = log_df[['machine_name', 'name', 'time', 'exc_class', 'exc_msg', 'level', 'type']]
    # Rename to adhere to columns in database
    log_df = log_df.rename(columns={'name': 'log_name'})
    log_df['time'] = pd.to_datetime(log_df['time'])
    # Cut off execution message if longer than 100 chars
    log_df['exc_msg'] = log_df['exc_msg'].apply(lambda x: x[:100])

    query = db.write_df_to_sql('logs', log_df, debug=True)
    res = mysqlconn.execute(query)
    log.debug(f'Query sent to database. Result shows {res.rowcount} rows affected.')

mysqlconn.close()

log.close()
