#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu import SlackTools, GIFSlice, Keys


fpath = os.path.join(os.path.expanduser('~'), *['Downloads', 'make-big', 'ahhhhlmao.gif'])

g = GIFSlice()
imgs = g.slice(fpath, 50)

i = g.arrange_imgs(imgs)
print(i)

# upload
okr_name = Keys().get_key('okr-name')
okr_cookie = Keys().get_key('slack-okrcookie')
okr_token = Keys().get_key('slack-okrtoken')
st = SlackTools(log.log_name, okr_name, okr_token, okr_cookie)


st.upload_emojis(os.path.dirname(fpath), announce=False)
