#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from kavalkilu import SlackBot
import pandas as pd


sb = SlackBot()

resp = sb.user.api_call(
    'channels.history',
    channel='CM376Q90F',
    count=1000
)
if resp['ok']:
    results = {}

    msgs = resp['messages']
    for msg in msgs:
        try:
            user = msg['user']
        except KeyError:
            user = msg['bot_id']
        txt_len = len(msg['text'])
        if user in results.keys():
            results[user]['msgs'].append(txt_len)
        else:
            # Apply new dict for new user
            results[user] = {'msgs': [txt_len]}

# Process messages
for k, v in results.items():
    results[k] = {
        'total_messages': len(v['msgs']),
        'avg_msg_len': sum(v['msgs']) / len(v['msgs'])
    }

res_df = pd.DataFrame(results).transpose()

res_df = res_df.reset_index()
res_df = res_df.rename(columns={'index': 'user'})
res_df['user'] = res_df['user'].apply(lambda x: '<@{}>'.format(x))
res_df['total_messages'] = res_df['total_messages'].astype(int)
res_df['avg_msg_len'] = res_df['avg_msg_len'].round(1)
