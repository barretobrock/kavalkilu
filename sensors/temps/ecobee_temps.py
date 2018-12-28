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

# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = datetime.now().strftime('%H%M')
log = Log('ecobee_temp_{}'.format(log_suffix), 'temp', log_lvl='INFO')
log.debug('Logging initiated')

temp_dict = oh.read_value('actualTemperature')
hum_dict = oh.read_value('actualHumidity')

ha_db = MySQLLocal('homeautodb')
conn = ha_db.engine.connect()
# Find upstairs location
location_resp = conn.execute('SELECT id FROM locations WHERE location = "upstairs_gen"')
for row in location_resp:
    print(row)
    loc_id = row['id']
    break

# Build a dictionary of the values we're moving around
val_dict = {
    'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'temp': temp_dict['state'],
    'hum': hum_dict['state'],
    'temp_db': 'temps',
    'hum_db': 'humidity',
    'loc': loc_id
}
# Write timestamp and temps to garage location
temp_ins_q = 'INSERT INTO {temp_db} (`loc_id`, `record_date`, `record_value`) ' \
             'VALUES ({loc}, "{ts}", {temp});'.format(**val_dict)
temp_log = conn.execute(temp_ins_q)
hum_ins_q = 'INSERT INTO {hum_db} (`loc_id`, `record_date`, `record_value`) ' \
             'VALUES ({loc}, "{ts}", {hum});'.format(**val_dict)
hum_log = conn.execute(hum_ins_q)
conn.close()

log.debug('Temp logging successfully completed.')

log.close()
