import json
import requests
import pandas as pd
from slacktools import BlockKitBuilder


zones = ['TXC453', 'TXZ192']
url_base = 'https://api.weather.gov/alerts/active/zone/{}'
bkb = BlockKitBuilder()

alerts_dict = {}
for zone in zones:
    resp = requests.get(url_base.format(zone))
    data = json.loads(resp.text)
    raw_alerts = data['features']
    if len(raw_alerts) > 0:
        for alert in raw_alerts:
            props = alert['properties']
            aid = props['id']
            # Clean the description
            desc = props['description'].split('*')
            if len(desc) > 3:
                desc = desc[3]
            else:
                desc = desc[-1]
            desc = desc.replace('\n', ' ').strip()
            alert_dict = {
                'start': pd.to_datetime(props['effective']).strftime('%F %T'),
                'end': pd.to_datetime(props['expires']).strftime('%F %T'),
                'severity': props['severity'],
                'event': props['event'],
                'title': props['headline'],
                'desc': desc
            }
            if aid not in alerts_dict.keys():
                # Build the alert text
                blocks = [
                    bkb.make_context_section(f'Incoming alert <@{"UM35HE6R5"}>!'),
                    bkb.make_block_divider(),
                    bkb.make_block_section([
                        '*`{event}`*({severity})\t\t `{start}` to `{end}`\n'.format(**alerts_dict),
                        '*{title}*\n{desc}'.format(**alerts_dict)
                    ])

                ]
                # Send alert

                # Save alert to the dict
                alerts_dict[aid] = alert_dict

