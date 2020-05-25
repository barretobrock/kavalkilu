#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Everything to record system-related stats"""
import subprocess
from subprocess import check_output, CalledProcessError
import psutil


class SysTools:
    """System-level tools"""

    def __init__(self):
        """Nothing to initialize, as these will just serve as a bundle"""
        pass

    def get_pids(self, process_name):
        """Get the process id of the process matching the pattern provided"""
        try:
            res = check_output(['pgrep', '-f', process_name])
        except CalledProcessError:
            # Likely no processes found
            return []

        if res != '':
            # Process into a list of pids
            pid_list = list(map(int, res))
            return pid_list
        return []

    def kill_pid(self, pid):
        """Kills process with certain pid"""
        if psutil.pid_exists(pid):
            print('PID {} found. Terminating'.format(pid))
            p = psutil.Process(pid)
            p.terminate()
        else:
            print('PID {} was not found.'.format(pid))
