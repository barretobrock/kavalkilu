#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kavalkilu.tools.sensors import PIRSensor
from kavalkilu.tools.light import HueBulb
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from datetime import datetime
import os


MOTION_PIN = 18
lights = ['Garage 1', 'Garage 2']

# Set up OpenHab connection
oh = OpenHab()
# Initiate Log
log = Log('garage_motion', os.path.abspath('/home/pi/logs'), 'motion')
log.debug('Logging initiated')

# Set up motion detector
md = PIRSensor(MOTION_PIN)
# Set up hue lights
light_list = []
for light in lights:
    light_list.append(HueBulb(light))

tripped = md.arm(sleep_sec=0.1, duration_sec=300)
if tripped is not None:
    for light in light_list:
        if not light.get_status():
            light.turn_on()
            # Log motion
            req = oh.update_value('Motion_Garaaz_PIR', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            log.debug('Motion detected at {:%Y-%m-%d %H:%M:%S}'.format(datetime.now()))
else:
    # Turn off the light if it's been on for the past 5 min cycle without any trips
    log.debug('No motion detected for this period.')
    for light in light_list:
        if light.get_status():
            light.turn_off()
            log.debug('Lights were on. Turned off')

log.debug('Logging variable left at: {}'.format(tripped))

log.close()
