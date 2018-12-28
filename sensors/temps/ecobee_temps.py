#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Method to collect temperature and other useful data from ecobee"""
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal
from datetime import datetime


# Initiate Openhab
oh = OpenHab()
LOC_ID = 3
VAL_TBLS = ['temps', 'humidity']

# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = datetime.now().strftime('%H%M')
log = Log('ecobee_temp_{}'.format(log_suffix), 'temp', log_lvl='INFO')
log.debug('Logging initiated')

temp_dict = oh.read_value('Temp_Upstairs')
hum_dict = oh.read_value('Hum_Upstairs')

ha_db = MySQLLocal('homeautodb')
conn = ha_db.engine.connect()

temp_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

conn.close()

log.debug('Temp logging successfully completed.')

log.close()
