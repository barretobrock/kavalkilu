"""A script to import pihole query data from a sqlite backup to mysqldb, mainly for Grafana use."""

import os
import sqlite3
import pandas as pd
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = pd.datetime.now().strftime('%H%M')
log = Log('pihole_db_{}'.format(log_suffix), 'pihole_db', log_lvl='INFO')
log.debug('Logging initiated')

# Set pihole backup location
backup_path = os.path.join(os.path.expanduser('~'), *['data', 'pihole-FTL.db.backup'])

# Enumerate pihole's status types, as per https://docs.pi-hole.net/ftldns/database/
status_types = pd.DataFrame([
    {
        'status_id': 0,
        'desc': 'Unknown status (not answered by forward destination)',
        'status': 'unknown'
    }, {
        'status_id': 1,
        'desc': 'Blocked by gravity.list',
        'status': 'blocked'
    }, {
        'status_id': 2,
        'desc': 'Permitted + forwarded',
        'status': 'permitted'
    }, {
        'status_id': 3,
        'desc': 'Permitted + replied to from cache',
        'status': 'permitted'
    }, {
        'status_id': 4,
        'desc': 'Blocked by wildcard',
        'status': 'blocked'
    }, {
        'status_id': 5,
        'desc': 'Blocked by black.list',
        'status': 'blocked'
    }
])
query_types = pd.DataFrame([
    {
        'type_id': 1,
        'type': 'A'
    }, {
        'type_id': 2,
        'type': 'AAAA'
    }, {
        'type_id': 3,
        'type': 'ANY'
    }, {
        'type_id': 4,
        'type': 'SRV'
    }, {
        'type_id': 5,
        'type': 'SOA'
    }, {
        'type_id': 6,
        'type': 'PTR'
    }, {
        'type_id': 7,
        'type': 'TXT'
    }
])

# Establish connection to PiholeDB
conn = sqlite3.connect(backup_path)
# Log into piholedb
db = MySQLLocal('piholedb')
mysqlconn = db.engine.connect()
# Get the latest entry in the mysql database
latest_entry_query = """
    SELECT record_date
    FROM piholedb.pihole_queries
    ORDER BY record_date DESC
    LIMIT 1
"""
latest_entry = pd.read_sql_query(latest_entry_query, mysqlconn)['record_date'].iloc[0]
#latest_entry = pd.datetime(2018, 12, 27)

# Extract the pihole info
pihole_query = """
    SELECT id
        , timestamp
        , client
        , domain
        , type AS type_int
        , status AS status_int
        , COUNT(domain) AS cnt
    FROM queries
    WHERE timestamp > {ts:.0f}
    GROUP BY timestamp
        , client
        , domain
""".format(ts=latest_entry.timestamp())
entries = pd.read_sql_query(pihole_query, conn)
# Include query status
entries = entries.merge(status_types[['status_id', 'status']], left_on='status_int', right_on='status_id')
# Include type of query
entries = entries.merge(query_types[['type_id', 'type']], left_on='type_int', right_on='type_id')
# Keep only columns that we need
entries = entries[['timestamp', 'client', 'domain', 'type', 'status', 'cnt']]
# Change column names
entries = entries.rename(columns={
    'timestamp': 'record_date',
    'client': 'ip',
    'type': 'record_type',
    'status': 'record_status',
    'cnt': 'query_cnt'
})
# Convert timestamps to ISO format
entries['record_date'] = pd.to_datetime(
    entries['record_date'], unit='s').dt.tz_localize('utc').dt.tz_convert('US/Central').dt.tz_localize(None)
entries['record_date'] = entries['record_date'].dt.strftime('%F %T')
# Write to MySQL db
log.info('Found {:.0f} logs to input to db'.format(entries.shape[0]))

if entries.shape[0] > 0:
    query = db.write_df_to_sql('pihole_queries', entries, debug=True)
    mysqlconn.execute(query)

conn.close()
mysqlconn.close()

log.close()
