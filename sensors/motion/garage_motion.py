#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detects motion in garage and turns on lights"""
from kavalkilu import PIRSensor, HueBulb, hue_lights, OpenHab, Log, MySQLLocal
from datetime import datetime


MOTION_PIN = 18
lights = [x for x in hue_lights if 'Garage' in x['hue_name']]

# Set up OpenHab connection
oh = OpenHab()
# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('garage_motion', 'motion', log_lvl='INFO')
log.debug('Logging initiated')

# Set up motion detector
md = PIRSensor(MOTION_PIN)
# Set up hue lights
for light_dict in lights:
    light_dict['hue_obj'] = HueBulb(light_dict['hue_name'])

tripped = md.arm(sleep_sec=0.1, duration_sec=300)
if tripped is not None:
    # Log motion
    trip_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    req = oh.update_value('Motion_Garaaz_PIR', trip_time)
    log.info('Motion detected at {}'.format(trip_time))
    for light_dict in lights:
        light = light_dict['hue_obj']
        if not light.get_status():
            light.turn_on()
            # Update light status in OH
            req = oh.update_value('{}_Switch'.format(light_dict['oh_item_prefix']), 'ON')
            log.info('{} was off.. Turned on'.format(light.light_obj.name))
    # Log motion into homeautodb
    # Connect
    ha_db = MySQLLocal('homeautodb')
    conn = ha_db.engine.connect()
    # Find garage location
    location_resp = conn.execute('SELECT id FROM locations WHERE location = "garage"')
    for row in location_resp:
        loc_id = row['id']
        break
    # Write timestamp to garage location
    insertion_query = 'INSERT INTO motions (`loc_id`, `record_date`) VALUES ({}, "{}")'.format(loc_id, trip_time)
    motion_log = conn.execute(insertion_query)
    conn.close()
else:
    # Turn off the light if it's been on for the past 5 min cycle without any trips
    log.debug('No motion detected for this period.')
    for light_dict in lights:
        light = light_dict['hue_obj']
        if light.get_status():
            light.turn_off()
            # Change bulb/group status to OFF in OpenHab
            req = oh.update_value('{}_Switch'.format(light_dict['oh_item_prefix']), 'OFF')
            log.info('{} was on.. Turned off'.format(light.light_obj.name))

log.debug('Logging variable left at: {}'.format(tripped))

log.close()
