#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from kavalkilu import Log, LogArgParser, SlackBot


log = Log('viktor', log_lvl=LogArgParser().loglvl)

sb = SlackBot()
try:
    sb.run_rtm()
except KeyboardInterrupt:
    log.debug('Script ended manually.')

log.close()
