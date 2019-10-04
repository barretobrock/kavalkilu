#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from kavalkilu import SlackBot

sb = SlackBot()

channel = '#test'
search_from = '2019-08-16 16:33'
msgs = sb.search_messages_by_date('#test', search_from)

for msg in msgs:
    sb.delete_message(msg)
