#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from speedtest import Speedtest
import pandas as pd
from kavalkilu.tools import Log, Paths


p = Paths()
logg = Log('speedtest.logger', 'speedtest', log_lvl='INFO')
logg.debug('Logging initiated')

# Load previous data
save_path = os.path.join(p.data_dir, 'speedtest_data.csv')

# Prep speedtest by getting nearby servers
speed = Speedtest()
speed.get_servers([])
speed.get_best_server()

down = speed.download()/1000000
up = speed.upload()/1000000

# put variables into pandas type dataframe
test = pd.DataFrame({
    'TIMESTAMP': pd.datetime.now().isoformat(),
    'DOWNLOAD': down,
    'UPLOAD': up,
}, index=[0])
# Enforce column order
test = test[['TIMESTAMP', 'DOWNLOAD', 'UPLOAD']]

# Append data to csv file
if os.path.exists(save_path):
    # Append
    test.to_csv(save_path, mode='a', header=False, index=False)
else:
    # Write
    test.to_csv(save_path, index=False)

logg.close()
