#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. If not, will arm the cameras"""
import os
from kavalkilu import camera_ips, Amcrest, Paths, Log
import requests
from requests.auth import HTTPDigestAuth


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('motion_toggle', log_lvl='DEBUG')
log.debug('Logging initiated')

p = Paths()
cred = p.key_dict['webcam_api']

res_list = []
# Check if mobile(s) are connected to LAN
for ip in ['192.168.0.12', '192.168.0.14']:
    resp = os.system('ping -c 1 {}'.format(ip))
    res_list.append(True if resp == 0 else False)

# Base url for toggling the motion detection
url_base = 'http://{ip}/cgi-bin/configManager.cgi?action=setConfig&MotionDetect[0].Enable={tf}'
cameras = []
for k, v in camera_ips.items():
    cameras.append({
        'name': k,
        'ip': v,
        'obj': Amcrest(v, p.key_dict['webcam_api'])
    })

if any(res_list):
    log.debug('One of two devices are currently in the network. Disabling motion detection.')
    # If any IP is connected, ensure that the motion detection is disabled
    for cam in cameras:
        if cam['obj'].camera.is_motion_detector_on():
            log.debug('Camera "{name}" is currently set to motion detection. Disabling'.format(**cam))
            # Send command to turn off motion detection
            r = requests.get(url_base.format(ip=cam['ip'], tf='false'),
                             auth=HTTPDigestAuth(cred['user'], cred['password']))
            # Check HTTP response
            if r.status_code != 200:
                log.error('Error in HTTP GET response. Status code {}'.format(r.status_code))
            else:
                log.debug('HTTP GET successful.')
else:
    # Otherwise, enable motion detection
    for cam in cameras:
        if not cam['obj'].camera.is_motion_detector_on():
            log.debug('Camera "{name}" currently does not have motion detection enabled. Enabling.'.format(**cam))
            # Send command to turn off motion detection
            r = requests.get(url_base.format(ip=cam['ip'], tf='true'),
                             auth=HTTPDigestAuth(cred['user'], cred['password']))
            # Check HTTP response
            if r.status_code != 200:
                log.error('Error in HTTP GET response. Status code {}'.format(r.status_code))
            else:
                log.debug('HTTP GET successful.')

log.close()