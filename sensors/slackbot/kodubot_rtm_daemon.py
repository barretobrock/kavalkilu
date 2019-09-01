#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import daemonize
from kavalkilu import SlackBot, Log, SysTools

# Initiate logging
log = Log('kodubot', log_lvl='DEBUG')
log.debug('Logging initiated.')

pid = '/tmp/kodubot.pid'

if __name__ == "__main__":
    s = SlackBot()
    st = SysTools()
    daemon = daemonize.Daemonize(app='kodubot', pid=pid, action=s.run_rtm, logger=log)
    if len(sys.argv) == 2:
        cmd = sys.argv[1]
        if 'start' == cmd:
            daemon.start()
        elif 'stop' == cmd:
            s.send_message('notifications', 'Shutting down for now! :sleepyparrot:')
            log.debug('Exiting daemon')
            daemon.exit()
            log.debug('Checking for existing instances')
            kodubot_pids = st.get_pids('kodubot_rtm_daemon')
            if len(kodubot_pids) > 0:
                for pid in kodubot_pids:
                    log.info('Killing pid: {}'.format(pid))
                    st.kill_pid(pid)

        else:
            print("Unknown command: {}".format(cmd))
            sys.exit(2)
        sys.exit(0)
    else:
        print("Usage: {} start|stop".format(sys.argv[0]))
        sys.exit(2)

