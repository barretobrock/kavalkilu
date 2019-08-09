#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import daemonize
from kavalkilu import SlackBot


pid = '/tmp/kodubot.pid'

if __name__ == "__main__":
    s = SlackBot()
    daemon = daemonize.Daemonize(app='kodubot', pid=pid, action=s.run_rtm)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.exit()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop" % sys.argv[0])
        sys.exit(2)

