#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Goes through log files for the given period and prepares them for import into a monitoring database"""
import os
import pandas as pd
from kavalkilu import Paths, Log


# Initiate logging (META!)
log = Log('log_remover', log_lvl='INFO')
log.debug('Logging initiated.')

p = Paths()
log_dir = p.log_dir

MAX_DAYS = 30

ts_limit = (pd.datetime.now() - pd.Timedelta('{} days'.format(MAX_DAYS))).timestamp()

log_df = pd.DataFrame()
for path, subdirs, files in os.walk(log_dir):
    for name in files:
        path = os.path.join(path, name)
        # Get timestamp of log file's latest modification
        file_ts = os.path.getmtime(path)
        if file_ts < ts_limit:
            # Remove the log file
            os.remove(path)

log.close()
