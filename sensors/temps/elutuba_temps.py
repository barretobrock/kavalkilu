#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read temperature and humidity from garage"""
from kavalkilu import DHTTempSensor as DHT, OpenHab, Log, MySQLLocal
# from kavalkilu.tools.sensors import DHTTempSensor as DHT
# from kavalkilu.tools.openhab import OpenHab
# from kavalkilu.tools.log import Log
# from kavalkilu.tools.databases import MySQLLocal
import pandas as pd


# Set the pin
TEMP_PIN = 4
LOC_ID = 7
# Name of object in OpenHab
oh_name = 'Elutuba'
VAL_TBLS = ['temps', 'humidity']

oh = OpenHab()
# Initiate Log, including a suffix to the log name to denote which instance of log is running
now = pd.datetime.now()
log = Log('elutuba_temp', 'temp', log_lvl='INFO')
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
ha_db = MySQLLocal('homeautodb')
conn = ha_db.engine.connect()

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

conn.close()

log.debug('Temp logging successfully completed.')

log.close()
