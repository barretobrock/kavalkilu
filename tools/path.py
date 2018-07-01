#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


class Paths:
    def __init__(self):
        # ip addresses
        self.pihole_ip = '192.168.0.5'
        self.server_ip = '192.168.0.5'
        self.huebridge_ip = '192.168.0.146'
        self.webcam_ip = '192.168.0.7'
        self.server_hostname = 'bobrock'
        # directories
        self.home_dir = os.path.expanduser("~")
        self.image_dir = os.path.join(self.home_dir, 'images')
        self.data_dir = os.path.join(self.home_dir, 'data')
        self.script_dir = os.path.join(self.home_dir, 'kavalkilu')
        self.log_dir = os.path.join(self.home_dir, 'logs')
        self.key_dir = os.path.join(self.home_dir, 'keys')
        # filepaths
        self.privatekey_path = os.path.join(os.path.expanduser('~'), *['.ssh', 'id_rsa'])
        self.google_client_secret = os.path.join(self.key_dir, 'client_secret.json')
        self.ip_path = os.path.join(self.key_dir, 'myip.txt')

        # key filepaths
        file_list = [
            'darksky_api.txt',
            'pushbullet_api.txt',
            'plotly_api.txt',
            'tweepy_api.txt',
            'personal_tweepy_api.txt',
            'webcam_api.txt',
        ]

        self.key_dict = {}

        for tfile in file_list:
            fpath = os.path.join(self.key_dir, tfile)
            if os.path.isfile(fpath):
                with open(fpath) as f:
                    self.key_dict[tfile.replace('.txt', '')] = f.read().replace('\n', '')
