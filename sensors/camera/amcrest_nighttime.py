#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Activates nighttime mode on cameras"""
from kavalkilu import SecCamGroup, Keys, Log, LogArgParser


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('cam_night', log_lvl=LogArgParser().loglvl)

cred = Keys().get_key('webcam_api')

# Instantiate all cameras
agroup = SecCamGroup(cred, log)

# This is for the evening, so let's enable motion detection for all devices
agroup.motion_toggler(motion_on=True)

log.close()
