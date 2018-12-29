"""Collect local temperature data"""

from kavalkilu.tools.weather import DarkSkyWeather
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal
import pandas as pd


local_latlong = '59.3311,26.2880'
LOC_ID = 10
dsky = DarkSkyWeather(local_latlong)

# Get a dataframe of the current weather
current_df = dsky.current_summary()

VAL_TBLS = ['temps', 'humidity', 'ozone', 'wind', 'pressure']
vals = ['temperature', 'humidity', 'ozone', 'windSpeed', 'pressure']
now = pd.datetime.now()

# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = now.strftime('%H%M')
log = Log('ecobee_temp_{}'.format(log_suffix), 'temp', log_lvl='INFO')
log.debug('Logging initiated')

ha_db = MySQLLocal('homeautodb')

# Build out a list of dataframes for each measurement to record
current_df['loc_id'] = LOC_ID
current_df = current_df.rename(columns={'time': 'record_date'})
current_df['humidity'] = current_df['humidity'] * 100

conn = ha_db.engine.connect()
for tbl, val in zip(VAL_TBLS, vals):
    # Prep the dataframe for writing the query
    df = current_df[['loc_id', 'record_date'] + [val]]
    df = df.rename(columns={val: 'record_value'})
    # Build query and execute
    query = ha_db.write_df_to_sql(tbl, df, debug=True)
    conn.execute(query)

conn.close()

log.debug('Temp logging successfully completed.')

log.close()
