#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from primary.maintools import Paths, CSVHelper
from logger.pylogger import Log


p = Paths()
logg = Log('obd.compacter', p.log_dir, 'obd_compacter', log_lvl="DEBUG")
logg.debug('Log initiated')

csvhelp = CSVHelper()

# Set path to compact csv files to
compact_path = os.path.join(p.data_dir, 'obd_results_main.csv')
file_glob = os.path.join(p.data_dir, 'obd_results_201*.csv')

# Compact the csv files
csvhelp.csv_compacter(compact_path, file_glob, sort_column='TIMESTAMP')

logg.debug('File compaction completed.')

logg.close()
