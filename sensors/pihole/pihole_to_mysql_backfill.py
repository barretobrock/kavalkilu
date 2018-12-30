"""A script to import pihole query data from a sqlite backup to mysqldb, mainly for Grafana use."""

import os
import sqlite3
import pandas as pd
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal, PiHoleDB


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('pihole_db_backfill', 'pihole_db', log_lvl='DEBUG')
log.debug('Logging initiated')


def get_latest_or_earliest_entry(conn, is_latest=True, is_pihole_db=False):
    """Gets the latest entry in the MySQLDB (to ensure we don't duplicate entries)
    Returns:
        pd.TimeStamp object
    """
    if is_latest:
        order = 'DESC'
    else:
        order = 'ASC'

    if is_pihole_db:
        # Get the latest / earliest entry in the sqlite database
        query = """
            SELECT timestamp
            FROM queries
            ORDER BY timestamp {}
            LIMIT 1
        """
    else:
        # Get the latest / earliest entry in the mysql database
        query = """
            SELECT record_date
            FROM piholedb.pihole_queries
            ORDER BY record_date {}
            LIMIT 1
        """
    df = pd.read_sql_query(query.format(order), conn)

    if df.empty:
        return None
    latest = df.iloc[0, 0]
    return latest


def convert_unix_to_dtt(obj, unit='s', tz='US/Central'):
    """Converts a UNIX timestamp object to datetime"""
    try:
        obj = pd.to_datetime(obj, unit=unit).dt.tz_localize('utc').dt.tz_convert(tz).dt.tz_localize(None)
    except AttributeError:
        # Not a dataframe
        obj = pd.to_datetime(obj, unit=unit)
        obj = obj.tz_localize('utc').tz_convert(tz).tz_localize(None)
    return obj


def prep_entries(df, status_df, type_df):
    """Prepares Pihole entry dataframe for insertion into MySQLDB"""

    # Include query status
    df = df.merge(status_df[['status_id', 'status']], left_on='status_int', right_on='status_id')
    # Include type of query
    df = df.merge(type_df[['type_id', 'type']], left_on='type_int', right_on='type_id')
    # Keep only columns that we need
    df = df[['timestamp', 'client', 'domain', 'type', 'status', 'cnt']]
    # Change column names
    df = df.rename(columns={
        'timestamp': 'record_date',
        'client': 'ip',
        'type': 'record_type',
        'status': 'record_status',
        'cnt': 'query_cnt'
    })
    # Convert timestamps to ISO format
    df['record_date'] = convert_unix_to_dtt(df['record_date'])
    df['record_date'] = df['record_date'].dt.strftime('%F %T')

    return df


# Set pihole backup location
backup_path = os.path.join(os.path.expanduser('~'), *['data', 'pihole-FTL.db.backup'])

# Enumerate pihole's status types, as per https://docs.pi-hole.net/ftldns/database/
status_types = pd.DataFrame(PiHoleDB.status_types)
query_types = pd.DataFrame(PiHoleDB.query_types)

# Establish connection to PiholeDB
conn = sqlite3.connect(backup_path)
# Log into piholedb
db = MySQLLocal('piholedb')
mysqlconn = db.engine.connect()
# Get the latest entry in the MySQLDB
latest_mysql_entry = get_latest_or_earliest_entry(mysqlconn)

earliest_pihole_entry = convert_unix_to_dtt(get_latest_or_earliest_entry(conn, False, True))
latest_pihole_entry = convert_unix_to_dtt(get_latest_or_earliest_entry(conn, True, True))

end_date_ranges = pd.date_range(earliest_pihole_entry, latest_pihole_entry, freq='D')
st_date_ranges = end_date_ranges.shift(-1)

date_ranges = [{
    'start': x.replace(hour=0, minute=0, second=0).timestamp(),
    'end': y.replace(hour=0, minute=0, second=0).timestamp()} for x, y in zip(st_date_ranges, end_date_ranges)]

for dt_rng in date_ranges:
    log.info('Beginning work on {:%F}'.format(convert_unix_to_dtt(dt_rng['start'])))
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
        WHERE timestamp BETWEEN {start:.0f} AND {end:.0f}
        GROUP BY timestamp
            , client
            , domain
        ORDER BY timestamp
    """.format(**dt_rng)
    entries = pd.read_sql_query(pihole_query, conn)
    entries = prep_entries(entries, status_types, query_types)

    # Write to MySQL db
    log.info('Found {:.0f} logs to input to db'.format(entries.shape[0]))

    if entries.shape[0] > 0:
        query = db.write_df_to_sql('pihole_queries', entries, debug=True)
        res = mysqlconn.execute(query)
        log.debug('Query sent to database. Result shows {} rows affected.'.format(res.rowcount))
    else:
        log.info('No new entries to be found. No querying to be done.')

log.debug('Closing connections.')
conn.close()
mysqlconn.close()

log.close()
