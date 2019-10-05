#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Goes through log files for the given period and prepares them for deletion :)
NOTE:
    To be run monthly
"""
import os
from datetime import datetime as dtime, timedelta as tdelta
from kavalkilu import Paths, Log, LogArgParser


# Initiate logging (META!)
log = Log('log_remover', log_lvl=LogArgParser().loglvl)
log.debug('Logging initiated.')

p = Paths()
log_dir = p.log_dir

MAX_DAYS = 30

ts_limit = (dtime.now() - tdelta(days=MAX_DAYS)).timestamp()

for path, subdirs, files in os.walk(log_dir):
    for name in files:
        path = os.path.join(path, name)
        # Get timestamp of log file's latest modification
        file_ts = os.path.getmtime(path)
        if file_ts < ts_limit:
            # Remove the log file
            log.info('Removing file {}'.format(name))
            os.remove(path)

log.close()
