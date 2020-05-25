#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu import Keys, Log, LogArgParser
from slacktools import SlackTools


log = Log('emoji.extraction', log_lvl=LogArgParser().loglvl)

moji_dir = os.path.join(os.path.expanduser('~'), *['Downloads', 'mojis'])

os.path.isdir(moji_dir)

okr_name = Keys().get_key('okr-name')
okr_cookie = Keys().get_key('slack-okrcookie')
okr_token = Keys().get_key('slack-okrtoken')
# too_name = Keys().get_key('too-name')
# too_token = Keys().get_key('slack-tootoken')
dnd_name = 'dd-indeed'
dnd_token = Keys().get_key('slack-dndtoken')
dnd_cookie = Keys().get_key('slack-dndcookie')

okr = SlackTools(log.log_name, team=okr_name, xoxp_token=okr_token, xoxb_token=okr_token, cookie=okr_cookie, triggers=['rrr'])
dnd = SlackTools(log.log_name, team=dnd_name, xoxp_token=dnd_token, xoxb_token=dnd_token, cookie=dnd_cookie, triggers=['rrr'])

# Make list of exact matches
exact_emojis = None
# list of fuzzy matches
fuzzy = '.*(dnd|str|dex|cha|wis|int|con|eyes|wtf|trig|poo|uwu|bi(^g)|smile|party|thonk).*'
# Collect from workspace
collected = okr.match_emojis(exact_emojis, fuzzy)

# Check against preexisting
emojis = dnd.get_emojis()
missing_emojis = {k: v for k, v in collected.items() if k not in emojis.keys()}
log.debug('{} emojis matched.'.format(len(missing_emojis)))

# Download
okr.download_emojis(missing_emojis, moji_dir)

# Upload emojis in folder
#   For large uploads, 5s wait is better
dnd.upload_emojis(moji_dir, wait_s=5, announce_channel='random')
