#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determines if mobile is connected to local network. If not, will arm the cameras"""
import os
from kavalkilu import Amcrest, AmcrestWeb, Paths


p = Paths()
res_list = []
# Check if mobile(s) are connected to LAN
for ip in ['192.168.0.12', '192.168.0.14']:
    resp = os.system('ping -c 1 {}'.format(ip))
    res_list.append(True if resp == 0 else False)

cameras = []
for k, v in cam_ips.items():
    cameras.append({
        'ip': v,
        'obj': Amcrest(v)
    })

if any(res_list):
    # If any IP is connected, ensure that the motion detection is disabled


else:
    # Otherwise, enable motion detection