#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu import Keys, Log, LogArgParser
from slacktools import SlackTools


log = Log('emoji.extraction', log_lvl=LogArgParser().loglvl)

moji_dir = os.path.join(os.path.expanduser('~'), *['Downloads', 'emojis'])

os.path.isdir(moji_dir)

okr_name = Keys().get_key('okr-name')
okr_cookie = Keys().get_key('slack-okrcookie')
okr_token = Keys().get_key('slack-okrtoken')
too_name = Keys().get_key('too-name')
too_token = Keys().get_key('slack-tootoken')

okr = SlackTools(log, team=okr_name, xoxp_token=okr_token, cookie=okr_cookie)
too = SlackTools(log, team=too_name, xoxp_token=too_token)

# Make list of exact matches
exact_emojis = None
# list of fuzzy matches
fuzzy = '.*(mood|cloud|skel|spook|pipe|chef|press|eyes|wtf|trig|poo|uwu|bi(^g)).*'
# Collect from workspace
collected = too.match_emojis(exact_emojis, fuzzy)

# Check against preexisting
emojis = okr.get_emojis()
missing_emojis = {k: v for k, v in collected.items() if k not in emojis.keys()}
log.debug('{} emojis matched.'.format(len(missing_emojis)))

# Download
too.download_emojis(missing_emojis, moji_dir)

# Upload emojis in folder
#   For large uploads, 5s wait is better
okr.upload_emojis(moji_dir, announce=True, wait_s=5)

