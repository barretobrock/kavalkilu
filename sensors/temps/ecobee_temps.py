#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Method to collect temperature and other useful data from ecobee"""
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal
from datetime import datetime
import os


# Initiate Openhab
oh = OpenHab()
UPSTAIRS_LOC = 3
VAL_TBLS = ['temps', 'humidity']

# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = datetime.now().strftime('%H%M')
log = Log('ecobee_temp_{}'.format(log_suffix), 'temp', log_lvl='INFO')
log.debug('Logging initiated')

temp_dict = oh.read_value('actualTemperature')
hum_dict = oh.read_value('actualHumidity')

ha_db = MySQLLocal('homeautodb')
conn = ha_db.engine.connect()

temp_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
temp_avg = temp_dict['state']
hum_avg = hum_dict['state']

# Build a dictionary of the values we're moving around
vals = [{'loc': UPSTAIRS_LOC, 'ts': temp_time, 'val': x, 'tbl': y} for x, y in zip([temp_avg, hum_avg], VAL_TBLS)]

for val_dict in vals:
    # For humidity and temp, insert into tables
    insert_query = """
        INSERT INTO {tbl} (`loc_id`, `record_date`, `record_value`)
        VALUES ({loc}, "{ts}", {val})
    """.format(**val_dict)
    insert_log = conn.execute(insert_query)

conn.close()

log.debug('Temp logging successfully completed.')

log.close()
