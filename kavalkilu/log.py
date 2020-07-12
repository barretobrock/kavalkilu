#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General log setup file.
"""
import os
import sys
import logging
import argparse
import traceback
from logging.handlers import TimedRotatingFileHandler
from types import TracebackType
from datetime import datetime as dt
from .influx import InfluxDBNames, InfluxTblNames, InfluxDBLocal
from .net import NetTools


class LogArgParser:
    """Simple class for carrying over standard argparse routines to set log level"""
    def __init__(self, is_debugging: bool = False):
        self.loglvl = 'INFO'    # Default
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-lvl', '--level', action='store', default='INFO')
        if is_debugging:
            print('Bypassing argument parser in test environment')
            self.loglvl = 'DEBUG'
        else:
            # Not running tests in PyCharm, so take in args
            self.args = self.parser.parse_args()
            # Convert args to dict to detect item
            arg_dict = vars(self.args)
            # Look for argument
            for k in ['lvl', 'level']:
                if k in arg_dict.keys():
                    self.loglvl = arg_dict[k].upper()
                    break


class Log:
    """Initiates a logging object to record processes and errors"""

    def __init__(self, log_name: str, child_name: str = None,
                 log_filename_prefix: str = None, log_dir: str = None,
                 log_lvl: str = None, log_to_db: bool = False):
        """
        Args:
            log_name: str, display name of the log. Will have the time (HHMM) added to the end
                to denote separate instances
            child_name: str, name of the child log.
                This is used when the log being made is considered a child to the parent log name
            log_filename_prefix: str, filename prefix (ex. 'npslog')
                default: log_name
            log_dir: str, directory to save the log
                default: "~/logs/{log_filename_prefix}/"
            log_lvl: str, minimum logging level to write to log (Hierarchy: DEBUG -> INFO -> WARN -> ERROR)
                default: 'INFO'
        """
        # Whether to log errors to database
        self.log_to_db = log_to_db
        # Set the group of the log (e.g., the type of script it'll be called from
        self.log_name_group = log_name
        # Name of log in logfile
        self.is_child = child_name is not None
        if self.is_child:
            # We've already had a logger set up,
            #   so find that and set this instance as a child of that instance
            self.logger = logging.getLogger(log_name).getChild(child_name)
        else:
            self.log_name = f'{log_name}_{dt.now():%H%M}'
            if log_filename_prefix is None:
                log_filename_prefix = log_name
            # Set name of file
            self.log_filename = f"{log_filename_prefix}_{dt.today():%Y%m%d}.log"
            # Set log directory (if none)
            home_dir = os.path.join(os.path.expanduser('~'), 'logs')
            if log_dir is None:
                log_dir = os.path.join(home_dir, log_name)
            else:
                log_dir = os.path.join(home_dir, log_dir)
            # Check if logging directory exists
            if not os.path.exists(log_dir):
                # If dir doesn't exist, create
                os.makedirs(log_dir)

            # Path of logfile
            self.log_path = os.path.join(log_dir, self.log_filename)
            # Create logger if it hasn't been created
            self.logger = logging.getLogger(self.log_name)

        # Check if debugging in pycharm
        # Checking Methods:
        #   1) checks for whether code run in-console
        #   2) check for script run in debug mode per PyCharm
        sysargs = sys.argv
        self.is_debugging = any(['pydevconsole.py' in sysargs[0], sys.gettrace() is not None])

        # Get minimum log level to record (Structure goes: DEBUG -> INFO -> WARN -> ERROR)
        if log_lvl is None:
            log_lvl = LogArgParser(self.is_debugging).loglvl
        self.logger_lvl = getattr(logging, log_lvl.upper(), logging.DEBUG)
        # Set minimum logging level
        self.logger.setLevel(self.logger_lvl)

        if not self.is_child:
            # Create file handler for log
            self._set_handlers()
        self.info(f'Logging initiated{" for child instance" if self.is_child else ""}.')

        if self.is_debugging and self.log_to_db:
            self.debug('Debug mode activated. Disabling influx db logging.')
            self.log_to_db = False

        if self.log_to_db and not self.is_debugging:
            # Only log errors if we're not debugging
            self.debug('Establishing connection to Influxdb.')
            self.machine = NetTools().get_hostname()
            # Set up influx object for logging errors
            self.influx = InfluxDBLocal(InfluxDBNames.HOMEAUTO)
        else:
            self.influx = None

    def _set_handlers(self):
        """Sets up file & stream handlers"""
        # TimedRotating will delete logs older than 30 days
        fh = TimedRotatingFileHandler(self.log_path, when='d', interval=1, backupCount=30)
        fh.setLevel(self.logger_lvl)
        # Create streamhandler for log (this sends streams to stdout/stderr for debug help)
        sh = logging.StreamHandler()
        sh.setLevel(self.logger_lvl)
        # Set format of logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s %(message)s')
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)
        # Add handlers to log
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)
        # Intercept exceptions
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type: type, exc_value: BaseException,
                         exc_traceback: TracebackType):
        """Intercepts an exception and prints it to log file"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        # Log error to influxdb
        self._log_error_to_influx("Uncaught exception", exc_value)

    def info(self, text: str):
        """Info-level logging"""
        self.logger.info(text)

    def debug(self, text: str):
        """Debug-level logging"""
        self.logger.debug(text)

    def warning(self, text: str):
        """Warn-level logging"""
        self.logger.warning(text)

    def _log_error_to_influx(self, text: str, err_obj: BaseException = None):
        """Logs an error to the database"""
        if self.log_to_db:
            err_txt = err_obj.__repr__() if err_obj is not None else text
            err_class = err_obj.__class__.__name__ if err_obj is not None else 'NA'
            log_dict = {
                'machine': self.machine,
                'name': self.log_name_group,
                'level': 'ERROR',
                'class': err_class,
                'text': err_txt
            }
            field_dict = {'entry': 1}
            self.influx.write_single_data(InfluxTblNames.LOGS,
                                          tag_dict=log_dict, field_dict=field_dict)
            self.debug('Logged error to influx.')

    def error(self, text: str, incl_info: bool = True):
        """Error-level logging"""
        self.logger.error(text, exc_info=incl_info)
        # Log error to influxdb
        self._log_error_to_influx(text)

    def error_with_class(self, err_obj: BaseException, text: str):
        """Error-level logging that also preserves the class of the error"""
        traceback_msg = '\n'.join(traceback.format_tb(err_obj.__traceback__))
        exception_msg = f'{err_obj.__class__.__name__}: {err_obj}\n\n{traceback_msg}'
        err_msg = f'{exception_msg}\n{text}'
        self.logger.error(err_msg)
        # Log error to influxdb
        self._log_error_to_influx(text, err_obj)

    def close(self):
        """Close logger"""
        disconn_msg = 'Log disconnected'
        if self.is_child:
            self.logger.info(f'{disconn_msg} for child instance.')
        else:
            self.logger.info(f'{disconn_msg}.\n' + '-' * 80)
            handlers = self.logger.handlers
            for handler in handlers:
                handler.close()
                self.logger.removeHandler(handler)
