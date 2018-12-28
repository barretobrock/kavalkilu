"""Read temperature and humidity from garage"""

from kavalkilu.tools.sensors import DHTTempSensor as DHT
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal
import pandas as pd


# Set the pin
TEMP_PIN = 24
LOC_ID = 2
# Name of object in OpenHab
oh_name = 'Garaaz'
VAL_TBLS = ['temps', 'humidity']

oh = OpenHab()
# Initiate Log, including a suffix to the log name to denote which instance of log is running
now = pd.datetime.now()
log_suffix = now.strftime('%H%M')
log = Log('garage_temp_{}'.format(log_suffix), 'temp', log_lvl='INFO')
log.debug('Logging initiated')
# Instantiate the temp sensor
tsensor = DHT(TEMP_PIN, decimals=3)

# Take 5 readings, 1 second apart and get average
avg_reading = tsensor.measure(n_times=5)
temp_time = now.strftime('%Y-%m-%d %H:%M:%S')
temp_avg, hum_avg = (avg_reading[k] for k in ['temp', 'humidity'])

# Update values in OpenHab
oh_values = {
    'Env_{}_Update'.format(oh_name): temp_time,
    'Temp_{}'.format(oh_name): temp_avg,
    'Hum_{}'.format(oh_name): hum_avg
}

for name, val in oh_values.items():
    req = oh.update_value(name, '{}'.format(val))

# Log motion into homeautodb
# Connect
ha_db = MySQLLocal('homeautodb')

# Build a dictionary of the values we're moving around
vals = [{'loc_id': LOC_ID, 'record_date': temp_time,
         'record_value': x, 'tbl': y} for x, y in zip([temp_avg, hum_avg], VAL_TBLS)]

for val_dict in vals:
    # For humidity and temp, insert into tables
    tbl = val_dict.pop('tbl')
    df = pd.DataFrame(val_dict, index=[0])
    ha_db.write_dataframe(tbl, df)

log.debug('Temp logging successfully completed.')

log.close()
