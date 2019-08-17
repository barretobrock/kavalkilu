#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import re
import pandas as pd


# These are extracted from browser session info
workspace = ''
x_id = ''
version_ts = ''
token = ''
cookie = ''

base_url = 'https://{}.slack.com/api/emoji.adminList'.format(workspace)
origin = base_url.split('/api')[0]
authority = origin.split('//')[1]
url = '{}?_x_id={}&slack_route=T029BFEQ3&_x_version_ts={}'.format(base_url, x_id, version_ts)
payload = {
    'page': 1,
    'count': 10000,
    'token': token,
    '_x_reason': 'customize-emoji-new-query',
    '_x_mode': 'online'
}
header = {
    'authority': authority,
    'accept': '*/*',
    'cookie': cookie,
    'origin': origin
}
resp = requests.post(url, data=payload, headers=header)
emoji = resp.json()['emoji']
len(emoji)

# Set download path
dl_path = os.path.join(os.path.abspath('/home/bobrock/'), *['Downloads', 'mojis'])


def match_specific(emoji_list, match_list):
    """Matches specific emojis"""
    matches = []
    for emoji in emoji_list:
        name = emoji['name']
        if name in match_list:
            matches.append(emoji)
    return matches


def regex_match(emoji_list, regex_str):
    """Matches specific emojis"""
    pattern = re.compile(regex_str, re.IGNORECASE)
    matches = []
    for emoji in emoji_list:
        name = emoji['name']
        if pattern.match(name) is not None:
            matches.append(emoji)
    return matches


def download_emojis(list_of_emojis, dl_dir):
    """Downloads a list of emojis"""
    for emoji in list_of_emojis:
        name = emoji['name']
        emoji_url = emoji['url']
        if emoji_url[:4] == 'data':
            data = emoji_url
        else:
            r = requests.get(emoji_url)
            data = r.content
        # Write pic to file
        fname = '{}{}'.format(name, os.path.splitext(emoji_url)[1])
        fpath = os.path.join(dl_dir, fname)
        write = 'wb' if isinstance(data, bytes) else 'w'
        with open(fpath, write) as f:
            f.write(data)


# Make list of exact matches
exact_emojis = ['wat']
# list of fuzzy matches
fuzzy = '.*(snoop|ow|whammy|noo|intensifies|trigger|shake|\d{3,}).*'

collected = match_specific(emoji, exact_emojis)
collected += regex_match(emoji, fuzzy)

download_emojis(collected, dl_path)

fuzzy = '.*(thonk).*'
collected += regex_match(emoji, fuzzy)
for i, item in enumerate(collected):
    name = item['name']
    name = name.replace('think', 'thonk')
    collected[i]['name'] = name

download_emojis(collected, dl_path)

print(''.join([':{}:'.format(x['name']) for x in collected]))
