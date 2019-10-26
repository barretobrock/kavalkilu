#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from slacktools import SlackTools
from kavalkilu import Log, LogArgParser, DarkSkyWeather


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('darksky', 'temp', log_lvl=LogArgParser().loglvl)

# Temp in C that serves as the floor of the warning
austin = '30.3428,-97.7582'
now = pd.datetime.now()

st = SlackTools(log)
dark = DarkSkyWeather(austin)

alerts = dark.get_alerts()

if alerts is not None:
    for i, row in alerts.iterrows():
        alert_dict = row.to_dict()
        # TODO: store alert by timestamp + title hash and don't send to channel again if there's no change
        msg = '<@{}> - Incoming Alert!\n`{title}`\nFrom: `{time}` to `{expires}`' \
              '\n{description}\n\n{uri}'.format('UM35HE6R5', **alert_dict)
        # st.send_message('notifications', msg)


log.close()
