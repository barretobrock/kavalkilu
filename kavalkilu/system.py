#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psutil
from subprocess import check_output, CalledProcessError
from typing import List, Union


class SysTools:
    """System-level tools"""

    def __init__(self):
        """Nothing to initialize, as these will just serve as a bundle"""
        pass

    @staticmethod
    def get_system_temps() -> dict:
        """Get the temperature of various sensors on the machine """
        sensor_temps = psutil.sensors_temperatures()
        # Build a dictionary of average sensor temperatures
        avg_temps = {}
        for k, v in sensor_temps.items():
            current_measurements = [x.current for x in v if x.current > 0]
            if len(current_measurements) == 0:
                continue
            avg_measurement = sum(current_measurements) / len(current_measurements)
            avg_temps[k] = avg_measurement
        if len(avg_temps) > 0:
            return avg_temps

    @staticmethod
    def get_cpu_percent() -> dict:
        """Gets CPU usage percentage"""
        cpu_use = psutil.cpu_percent()
        return {'cpu-use': cpu_use}

    @staticmethod
    def get_mem_data():
        """Gets memory usage data (in MBs)"""
        ram = psutil.virtual_memory()
        return {
            'ram-total': ram.total / 2 ** 20,
            'ram-used': ram.used / 2 ** 20,
            'ram-free': ram.free / 2 ** 20,
            'ram-percent_used': ram.percent / 100
        }

    @staticmethod
    def get_disk_data():
        """Gets disk usage data (in GBs)"""
        disk = psutil.disk_usage('/')
        return {
            'disk-total': disk.total / 2 ** 30,
            'disk-used': disk.used / 2 ** 30,
            'disk-free': disk.free / 2 ** 30,
            'disk-percent_used': disk.percent / 100
        }

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
