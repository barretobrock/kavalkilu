"""Collect local temperature data"""

from kavalkilu.tools.weather import DarkSkyWeather
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal
import pandas as pd


local_latlong = '30.3428,-97.7582'
dsky = DarkSkyWeather(local_latlong)

# Get a dataframe of the current weather
current_df = dsky.current_summary()

# Initiate Openhab
oh = OpenHab()
LOC_ID = 8
VAL_TBLS = ['temps', 'humidity']
now = pd.datetime.now()

# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = now.strftime('%H%M')
log = Log('ecobee_temp_{}'.format(log_suffix), 'temp', log_lvl='INFO')
log.debug('Logging initiated')

temp_dict = oh.read_value('Temp_Upstairs')
hum_dict = oh.read_value('Hum_Upstairs')

ha_db = MySQLLocal('homeautodb')
conn = ha_db.engine.connect()


temp_time = now.strftime('%Y-%m-%d %H:%M:%S')
temp_avg = round(float(temp_dict['state']), 2)
hum_avg = round(float(hum_dict['state']), 2)

# Build a dictionary of the values we're moving around
vals = [{'loc_id': LOC_ID, 'record_date': temp_time,
         'record_value': x, 'tbl': y} for x, y in zip([temp_avg, hum_avg], VAL_TBLS)]

for val_dict in vals:
    # For humidity and temp, insert into tables
    insert_query = """
        INSERT INTO {tbl} (`loc_id`, `record_date`, `record_value`)
        VALUES ({loc_id}, "{record_date}", {record_value})
    """.format(**val_dict)
    insert_log = conn.execute(insert_query)


df = dsky.current_summary()
df['loc_id'] = LOC_ID
df = df[['loc_id', 'time', 'temperature']]
df = df.rename(columns={
    'time': 'record_date',
    'temperature': 'record_value'
})
df = df.append(df)



conn.close()

log.debug('Temp logging successfully completed.')

log.close()
