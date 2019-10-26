#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu import Keys
from slacktools import SlackTools


moji_dir = os.path.join(os.path.expanduser('~'), *['Downloads', 'mojis'])

okr_name = Keys().get_key('okr-name')
okr_cookie = Keys().get_key('slack-okrcookie')
okr_token = Keys().get_key('slack-okrtoken')
too_name = Keys().get_key('too-name')
too_token = Keys().get_key('slack-tootoken')

okr = SlackTools(okr_name, okr_token, okr_cookie)
too = SlackTools(too_name, too_token)

# Make list of exact matches
exact_emojis = None
# list of fuzzy matches
fuzzy = '.*().*'

# Collect from workspace
collected = too.match_emojis(exact_emojis, fuzzy)

# Check against preexisting
emojis = okr.get_emojis()
missing_emojis = {k: v for k, v in collected.items() if k not in emojis.keys()}

# Download
too.download_emojis(missing_emojis, moji_dir)

# Upload emojis in folder
#   For large uploads, 5s wait is better
okr.upload_emojis(moji_dir, announce=True, wait_s=5)

