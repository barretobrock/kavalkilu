#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psutil
from subprocess import check_output, CalledProcessError
from typing import List, Union, Optional


class SysTools:
    """System-level tools"""

    def __init__(self):
        """Nothing to initialize, as these will just serve as a bundle"""
        pass

    @staticmethod
    def get_pids(process_name: str) -> Union[List, List[int]]:
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

    @staticmethod
    def kill_pid(pid: int):
        """Kills process with certain pid"""
        if psutil.pid_exists(pid):
            print(f'PID {pid} found. Terminating')
            p = psutil.Process(pid)
            p.terminate()
        else:
            print(f'PID {pid} was not found.')
