#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read temperature and humidity from living room"""
from kavalkilu import DHTTempSensor as DHT, Log, SensorLogger


log = Log('elutuba_temp', 'temp', log_lvl='INFO')
# Set the pin
TEMP_PIN = 4
sl = SensorLogger('living_room', DHT(TEMP_PIN, decimals=3))
# Take in readings, update openhab & mysql data sources
sl.update()

log.debug('Temp logging successfully completed.')

log.close()
