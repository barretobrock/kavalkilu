#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from collections import OrderedDict
from urllib.request import urlopen
from kavalkilu.tools import Paths, DateTools, Log
from kavalkilu.tools.databases import CSVHelper
from kavalkilu.tools.message import PBullet


p = Paths()
# initiate logging
logg = Log('severe_weather', 'sevweather', log_lvl='DEBUG')
logg.debug('Logger initiated.')

ds_api = p.key_dict['darksky_api']
pb_api = p.key_dict['pushbullet_api']

dtools = DateTools()
csvhelp = CSVHelper()
pb = PBullet(pb_api)

# set location for query (home)
loc = p.home_loc

logg.debug('Loading previous alert file')
prev_alerts_path = os.path.join(p.data_dir, 'previous_alerts.csv')

url = "https://api.darksky.net/forecast/{}/{}?units=si&exclude=currently,flags".format(ds_api, loc)
logg.debug('Fetching DarkSky data from url: {}'.format(url))
darkskydata = urlopen(url).read().decode('utf-8')
data = json.loads(darkskydata)

# collect info on weather alerts
alerts = data.get('alerts')
if alerts is not None:
    logg.debug('Alerts fetched:{}'.format(len(alerts)))
    if os.path.exists(prev_alerts_path):
        prev_alerts = csvhelp.csv_to_ordered_dict(prev_alerts_path)
    else:
        prev_alerts = None

    for alert in alerts:
        title = alert['title']
        regions = alert['regions']
        desc = alert['description']
        time_reported = dtools.unix_to_string(alert['time'], '%Y%m%d_%H%M%S')
        expires = dtools.unix_to_string(alert['expires'], '%Y%m%d_%H%M%S')
        expires_formatted = dtools.unix_to_string(alert['expires'], '%Y-%m-%d %H:%M:%S')
        if prev_alerts is not None:
            if not any(['{}-{}'.format(d['title'], d['reported']) == '{}-{}'.format(title, time_reported) for d in prev_alerts]):
                # if no matches in previous alerts file...
                # ... add new alerts to that file and send message
                new_alert_dict = OrderedDict((
                    ('title', title),
                    ('reported', time_reported),
                    ('expiration', expires),
                ))
                pb.send_message('{} until {}'.format(title, expires_formatted), desc)
                # Add new alert dict to list
                prev_alerts.append(new_alert_dict)
                # Rewrite file to disk
                csvhelp.ordered_dict_to_csv(prev_alerts, prev_alerts_path)
else:
    logg.debug('No alerts found, ending.')


logg.close()
sys.exit()

