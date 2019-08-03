#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commonly-used paths
    NOTE: IP addresses found in /etc/hosts
"""

import os
import json
import re


class Paths:
    def __init__(self):
        # ip addresses
        self.server_hostname = 'bobrock'
        self.server_ip = '192.168.0.5'
        self.pihole_ip = self.server_ip
        self.openhab_ip = self.server_ip

        # directories
        self.home_dir = os.path.expanduser("~")
        self.image_dir = os.path.join(self.home_dir, 'images')
        self.data_dir = os.path.join(self.home_dir, 'data')
        self.script_dir = os.path.join(self.home_dir, 'kavalkilu')
        self.log_dir = os.path.join(self.home_dir, 'logs')
        self.key_dir = os.path.join(self.home_dir, 'keys')
        # filepaths
        self.privatekey_path = os.path.join(os.path.expanduser('~'), *['.ssh', 'id_rsa'])
        self.ip_path = os.path.join(self.key_dir, 'myip.txt')

