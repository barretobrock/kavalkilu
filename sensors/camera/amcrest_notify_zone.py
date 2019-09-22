#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. If not, will arm the cameras"""
import os
from kavalkilu import SecCamGroup, Keys, Log, Hosts


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('cam_active', log_lvl='INFO')
log.debug('Logging initiated')

cred = Keys().get_key('webcam_api')

res_list = []
# Check if mobile(s) are connected to LAN
for ip in [i['ip'] for i in Hosts().get_hosts('an_[bm]a.*')]:
    resp = os.system('ping -c 1 {}'.format(ip))
    res_list.append(True if resp == 0 else False)

# Instantiate all cameras
agroup = SecCamGroup(cred, log)

if any(res_list):
    log.debug('One of two devices are currently in the network. Disabling motion detection.')
    # If any IP is connected, ensure that the motion detection is disabled
    agroup.motion_toggler(motion_on=False)
else:
    # Otherwise, enable motion detection
    agroup.motion_toggler(motion_on=True)

log.close()
