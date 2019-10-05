#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detects whether the garage door is up or down"""
import pandas as pd
from kavalkilu import DistanceSensor, Log, LogArgParser, SlackBot, MySQLLocal


logg = Log('garage_door', 'gdoor', log_lvl=LogArgParser().loglvl)
TRIGGER_PIN = 23
ECHO_PIN = 24
logg.debug('Initializing sensor...')
ds = DistanceSensor(TRIGGER_PIN, ECHO_PIN)
sb = SlackBot()

# Take an average of 10 readings
readings = []
logg.debug('Taking readings...')
for i in range(10):
    readings.append(ds.measure())

avg = sum(readings) / len(readings)

# Collect last reading from database
eng = MySQLLocal('homeautodb')

garage_status_query = """
SELECT
    d.name
    , d.status
    , d.status_chg_date
    , d.update_date
FROM
    doors AS d
WHERE
    name = 'garage'
"""
garage_status = pd.read_sql_query(garage_status_query, con=eng.connection)

# Typically, reading is ca. 259cm when door is closed. ca. 50cm when open
if avg < 6000:
    logg.debug('Door is open. Reading of {}'.format(avg))
    status = 'OPEN'
else:
    logg.debug('Door is closed. Reading of {}'.format(avg))
    status = 'CLOSED'

if garage_status['status'] != status:
    # This is probably the first time
    sb.send_message('notifications', 'Garage door is now `{}`.'.format(status.lower()))
    # Record change in database
    garage_set_query = """
        UPDATE
            doors
        SET
            status = '{}'
            , update_date = NOW()
            , status_chg_date = NOW()
        WHERE
            name = 'garage'
    """.format(status)
else:
    # Otherwise just update the timestamp when last checked
    garage_set_query = """
        UPDATE
            doors
        SET
            update_date = NOW()
        WHERE
            name = 'garage'
    """
eng.write_sql(garage_set_query)

logg.close()
