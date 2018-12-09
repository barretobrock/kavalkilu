#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu.tools import Paths, FileSCP, Log
import glob


p = Paths()
logg = Log('obd.uploader', p.log_dir, 'obd_uploader', log_lvl="DEBUG")
logg.debug('Log initiated')

fscp = FileSCP(p.privatekey_path, p.server_ip, p.server_hostname)

# Set directory to put csv files after transfer to server computer
target_dir = os.path.abspath('/home/{}/data'.format(p.server_hostname))

# Find all csv files in data folder relating to obd
list_of_files = glob.glob("{}/obd_results*.csv".format(p.data_dir))
logg.debug('{} files total. Beginning transfer.'.format(len(list_of_files)))
if len(list_of_files) > 0:
    for csvfile in list_of_files:
        target_path = os.path.join(target_dir, os.path.basename(csvfile))
        # Transfer file
        fscp.scp_transfer(csvfile, target_path, is_remove_file=True)
        logg.debug('Successfully uploaded {}'.format(os.path.basename(csvfile)))

logg.close()
