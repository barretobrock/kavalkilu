#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import re
import time
from slackclient import SlackClient


# These are extracted from browser session info
# Must start with 'xoxs..'
okrtoken = ''
indeedtoken = ''

# For uploading
team_name = ''
cookie = ''

UPLOAD_WAIT_TIME_S = 2

URL_CUSTOMIZE = "https://{team_name}.slack.com/customize/emoji"
URL_ADD = "https://{team_name}.slack.com/api/emoji.add"
URL_LIST = "https://{team_name}.slack.com/api/emoji.adminList"

indeedsb = SlackClient(token=indeedtoken)
okr_sb = SlackClient(token=okrtoken)
emoji = indeedsb.api_call('emoji.list')['emoji']

# Set download path
dl_path = os.path.join(os.path.abspath('/home/bobrock/'), *['Downloads', 'mojis'])


def match_specific(emoji_dict, match_list):
    """Matches specific emojis"""
    matches = {}
    for k, v in emoji_dict.items():
        if k in match_list:
            matches[k] = v
    return matches


def regex_match(emoji_dict, regex_str):
    """Matches specific emojis"""
    pattern = re.compile(regex_str, re.IGNORECASE)
    matches = {}
    for k, v in emoji_dict.items():
        if pattern.match(k) is not None:
            matches[k] = v
    return matches


def download_emojis(dict_of_emojis, dl_dir):
    """Downloads a list of emojis"""
    for k, v in dict_of_emojis.items():
        if v[:4] == 'data':
            data = v
        elif v[:4] == 'http':
            r = requests.get(v)
            data = r.content
        else:
            continue
        # Write pic to file
        fname = '{}{}'.format(k, os.path.splitext(v)[1])
        fpath = os.path.join(dl_dir, fname)
        write = 'wb' if isinstance(data, bytes) else 'w'
        with open(fpath, write) as f:
            f.write(data)


def _session():
    assert cookie, "Cookie required"
    assert team_name, "Team name required"
    session = requests.session()
    session.headers = {'Cookie': cookie}
    session.url_customize = URL_CUSTOMIZE.format(team_name=team_name)
    session.url_add = URL_ADD.format(team_name=team_name)
    session.url_list = URL_LIST.format(team_name=team_name)
    session.api_token = okrtoken
    return session


def upload_emoji(session, emoji_name, filename):
    data = {
        'mode': 'data',
        'name': emoji_name,
        'token': session.api_token
    }
    files = {'image': open(filename, 'rb')}
    r = session.post(session.url_add, data=data, files=files, allow_redirects=False)
    r.raise_for_status()

    # Slack returns 200 OK even if upload fails, so check for status.
    response_json = r.json()
    if not response_json['ok']:
        print("Error with uploading {}: {}".format(emoji_name, response_json))
    return response_json['ok']


# Make list of exact matches
exact_emojis = ['trivial', 'minor', 'major', 'blocker']
# list of fuzzy matches
fuzzy = '.*(yeet|oink|horror|panic|snap|thumb|uwu|homer|drool|eye|rofl|lmao|intense|guy|man|sad|rage|cry|stonk|hyper|party|emoji|ic[ek]|blank|burn).*'

collected = match_specific(emoji, exact_emojis)
collected.update(regex_match(emoji, fuzzy))

# Check collected emojis against what we already have in OKR
okr_emojis = okr_sb.api_call('emoji.list')['emoji']
missing_emojis = {k: v for k, v in collected.items() if k not in okr_emojis.keys()}

download_emojis(missing_emojis, dl_path)

# Upload process here
session = _session()
successfully_uploaded = []
for k, v in missing_emojis.items():
    if k in successfully_uploaded or 'alias' in v:
        continue
    fname = '{}{}'.format(k, os.path.splitext(v)[1])
    fpath = os.path.join(dl_path, fname)
    successful = upload_emoji(session, k, fpath)
    if successful:
        # pop out of dict
        successfully_uploaded.append(k)
    # Wait
    print(':{}: successful - {:.2%} done'.format(k, len(successfully_uploaded) / len(missing_emojis)))
    time.sleep(5)

# Report the emojis captured to the channel
# 30 emojis per line, 5 lines per post
out_str = '\n'
cnt = 0
for item in successfully_uploaded:
    out_str += ':{}:'.format(item)
    cnt += 1
    if cnt % 30 == 0:
        out_str += '\n'
    if cnt == 150:
        okr_sb.api_call(
            'chat.postMessage',
            channel='emoji_suggestions',
            text=out_str
        )
        out_str = '\n'
        cnt = 0



