#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. If not, will arm the cameras"""
from kavalkilu import AmcrestGroup, Keys, Log


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('motion_toggle', log_lvl='DEBUG')
log.debug('Logging initiated')

cred = Keys().get_key('webcam_api')

# Instantiate all cameras
agroup = AmcrestGroup(cred, log)

# This is for the evening, so let's enable motion detection for all devices
agroup.motion_toggler(motion_on=True)

log.close()
