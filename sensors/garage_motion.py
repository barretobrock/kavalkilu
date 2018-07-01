#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kavalkilu.tools.sensors import PIRSensor
from kavalkilu.tools.light import HueBulb


MOTION_PIN = 18
lights = ['Garage 1', 'Garage 2']

# Set up motion detector
md = PIRSensor(MOTION_PIN)
# Set up hue lights
light_list = []
for light in lights:
    light_list.append(HueBulb(light))

tripped = md.arm(sleep_sec=0.1, duration_sec=300)
if tripped:
    for light in light_list:
        if not light.status:
            light.turn_on()
else:
    # Turn off the light if it's been on for the past 5 min cycle without any trips
    for light in light_list:
        if light.status:
            light.turn_off()

