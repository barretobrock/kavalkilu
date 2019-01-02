"""Goes through log files for the given period and prepares them for import into a monitoring database"""

import os
import re
import socket
import pandas as pd
from kavalkilu.tools.path import Paths
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal


# Initiate logging (META!)
log = Log('log_collector', log_lvl='DEBUG')
log.debug('Logging initiated.')


def read_log_file(log_path, log_dict):
    """Determine which log parsing method to use and build out a mapping of the log"""

    with open(log_path, 'r') as file:
        # Set empty log type before we try to determine it
        lines = file.readlines()

    for k in log_dict.keys():
        if log_dict[k]['compiled'].search(lines[0]) is not None:
            # Use these predetermined patterns to parse through the log
            log_patterns = log_dict[k]
            break

    # Begin log parsing
    output_list = []
    for line in lines:
        match = log_patterns['compiled'].match(line)
        if match is not None:
            match_str = match.group(0)
            match_list = match_str.split(' - ')

            log_name = match_list[1]
            if re.match('\d{4}', log_name.split('_')[-1]):
                # Timestamp in log name. remove it
                log_name = log_name[:-5]

            output_list.append({
                'time': pd.to_datetime(match_list[0]),
                'name': log_name,
                'level': match_list[2].split(' ')[0],
                'type': log_patterns['type']
            })

    return output_list


p = Paths()
log_dir = p.log_dir
machine_name = socket.gethostname()

handler_dict = {
    'py_log': {
        'type': 'py',
        'regex': '^\d+\-\d+\-\d+\s\d+\:\d+\:\d+\,\d+\s\-\s.*'
    },
    'sh_log': {
        'type': 'sh',
        'regex': '^\d+\-\d+\-\d+\_\d+\:\d+\:\d+\s\:+\s.*'
    }
}

# Include the compiler
for k, v in handler_dict.items():
    handler_dict[k]['compiled'] = re.compile(v['regex'])

today_str = pd.datetime.now().strftime('%Y%m%d')

log_df = pd.DataFrame()
for path, subdirs, files in os.walk(log_dir):
    for name in files:
        path = os.path.join(path, name)
        if today_str in name:
            # Continue with parsing current file
            logged_list = read_log_file(path, handler_dict)
            if len(logged_list) > 0:
                log_df = log_df.append(pd.DataFrame(logged_list))

if not log_df.empty:
    # Begin process to record to database
    # Establish order of log data
    log_df['machine_name'] = machine_name
    log_df = log_df[['machine_name', 'name', 'time', 'level', 'type']]
    # Rename to adhere to columns in database
    log_df = log_df.rename(columns={'name': 'log_name'})

    # Establish connection with database
    # Log into piholedb
    db = MySQLLocal('piholedb')
    mysqlconn = db.engine.connect()
    query = db.write_df_to_sql('logdb', log_df, debug=True)
    res = mysqlconn.execute(query)
    log.debug('Query sent to database. Result shows {} rows affected.'.format(res.rowcount))
    mysqlconn.close()

log.close()
