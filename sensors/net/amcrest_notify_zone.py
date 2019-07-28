#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. If not, will arm the cameras"""
import os
from kavalkilu import camera_ips, Amcrest, Paths, Log


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('motion_toggle', log_lvl='DEBUG')
log.debug('Logging initiated')


def motion_toggler(camera_list, motion_on, logg=None):
    """Handles the processes of toggling the camera's motion detection

    Args:
        camera_list: list of Amcrest-class camera objects
        motion_on: bool, if True, will turn motion detection to ON
        logg: Log object for writing messages to log.
    """
    for cam in camera_list:
        if cam.camera.is_motion_detector_on() != motion_on:
            if motion_on:
                log_txt = 'Camera "{}" currently does not have motion detection enabled. Enabling.'
            else:
                log_txt = 'Camera "{}" is currently set to motion detection. Disabling'
            logg.debug(log_txt.format(cam.name))
            # Send command to turn on motion detection
            resp = cam.toggle_motion(set_motion=motion_on)

            # Check HTTP response
            if resp.status_code != 200:
                logg.error('Error in HTTP GET response. Status code {}'.format(resp.status_code))
            else:
                logg.debug('HTTP GET successful.')


p = Paths()
cred = p.key_dict['webcam_api']

res_list = []
# Check if mobile(s) are connected to LAN
for ip in ['192.168.0.12', '192.168.0.14']:
    resp = os.system('ping -c 1 {}'.format(ip))
    res_list.append(True if resp == 0 else False)

cameras = []
for k, v in camera_ips.items():
    cameras.append(Amcrest(v, cred, name=k))

if any(res_list):
    log.debug('One of two devices are currently in the network. Disabling motion detection.')
    # If any IP is connected, ensure that the motion detection is disabled
    motion_toggler(cameras, motion_on=False, logg=log)

else:
    # Otherwise, enable motion detection
    motion_toggler(cameras, motion_on=True, logg=log)

log.close()
