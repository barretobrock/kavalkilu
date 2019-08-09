#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. If not, will arm the cameras"""
import os
import subprocess
from kavalkilu import Keys, Log, Hosts


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('device_connected', log_lvl='DEBUG')
log.debug('Logging initiated')

phone = Hosts().get_host('an_barret')['ip']
# Ping phone's ip and check response
resp = subprocess.call(['ping', '-c', '1', phone])

# pull last_ping for device from db here
# if last ping was greater than 5 mins, change status

if resp == 0:
    # Successfully pinged phone, check against db




log.close()
