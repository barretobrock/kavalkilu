#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tools.sensors import PIRSensor

MOTION_PIN = 3

# Set up motion detector
md = PIRSensor(MOTION_PIN)

md.arm()