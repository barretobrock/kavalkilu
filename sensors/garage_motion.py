#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kavalkilu.tools.sensors import PIRSensor
from kavalkilu.tools.light import HueBulb, hue_lights
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from datetime import datetime
import os


MOTION_PIN = 18
lights = [x for x in hue_lights if 'Garage' in x['hue_name']]

# Set up OpenHab connection
oh = OpenHab()
# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = datetime.now().strftime('%H%M')
log = Log('garage_motion_{}'.format(log_suffix), os.path.abspath('/home/pi/logs'), 'motion')
log.debug('Logging initiated')

# Set up motion detector
md = PIRSensor(MOTION_PIN)
# Set up hue lights
for light_dict in lights:
    light_dict['hue_obj'] = HueBulb(light_dict['hue_name'])

tripped = md.arm(sleep_sec=0.1, duration_sec=300)
if tripped is not None:
    # Log motion
    req = oh.update_value('Motion_Garaaz_PIR', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log.info('Motion detected at {:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
    for light_dict in lights:
        light = light_dict['hue_obj']
        if not light.get_status():
            light.turn_on()
            # Update light status in OH
            req = oh.update_value('{}_Switch'.format(light_dict['oh_item_prefix']), 'ON')
            log.info('{} was off.. Turned on'.format(light.light_obj.name))
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
