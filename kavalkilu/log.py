#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General log setup file.
"""
import sys
from logging import Logger, ERROR
from typing import Union
from easylogger import Log
from .influx import InfluxDBHomeAuto, InfluxDBLocal
from .net import NetTools


class LogWithInflux(Log):
    """Logging object that supports error logging to local Influxdb instance"""
    def __init__(self, log: Union[str, 'Log', Logger] = None, child_name: str = None, log_level_str: str = None,
                 log_to_file: bool = True, log_dir: str = None, log_to_db: bool = True):
        super().__init__(log=log, child_name=child_name, log_level_str=log_level_str, log_to_file=log_to_file,
                         log_dir=log_dir)
        self.log_to_db = log_to_db
        self.machine = NetTools().get_hostname()
        self.influx = None
        if self.is_debugging and self.log_to_db:
            self.debug('Debug mode activated. Disabling influx db logging.')

        if self.log_to_db and not self.is_debugging:
            # Only log errors if we're not debugging
            self.debug('Establishing connection to Influxdb.')
            # Set up influx object for logging errors
            self.influx = InfluxDBLocal(InfluxDBHomeAuto.LOGS)

        # Reset the exception hook
        sys.excepthook = self.handle_exception
        self.error = self.error_with_influx

    def error_with_influx(self, text: str, *args, **kwargs):
        self.log_obj.log(ERROR, msg=text, *args, **kwargs)
        err_type, err_obj, err_traceback = kwargs.pop('exc_info', (None, None, None))
        # Log error to influxdb
        self._log_error_to_influx(text, err_obj)

    def error_from_class(self, err_obj: BaseException, text: str):
        self._error_from_class(err_obj=err_obj, text=text)
        # Log error to influxdb
        self._log_error_to_influx(text, err_obj)

    def _log_error_to_influx(self, text: str, err_obj: BaseException = None):
        """Logs an error to the database"""
        if self.log_to_db and not self.is_debugging:
            err_txt = err_obj.__repr__() if err_obj is not None else text
            err_class = err_obj.__class__.__name__ if err_obj is not None else 'NA'
            log_dict = {
                'machine': self.machine,
                'name': self.log_name,
                'level': 'ERROR',
                'class': err_class,
                'text': err_txt
            }
            field_dict = {'entry': 1}
            self.influx.write_single_data(tag_dict=log_dict, field_dict=field_dict)
            self.debug('Logged error to influx.')
