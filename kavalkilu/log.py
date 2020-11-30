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
from typing import List, Dict, Union, Tuple, Optional
from .influx import InfluxDBNames, InfluxTblNames, InfluxDBLocal
from .net import NetTools


class ArgParse(argparse.ArgumentParser):
    """Custom wrapper for argument parsing"""
    def __init__(self, arg_list: List[Dict[str, Union[dict, List[str]]]], parse_all: bool = True):
        """
        Args:
            arg_list: List of the flags for each argument
                typical setup:
                >>> arg = [
                >>>     {
                >>>         'names': ['-l', '--level'],
                >>>         'other': {  # These are just the additional params available for add_argument
                >>>             'action': 'store',
                >>>             'default': 'INFO'
                >>>         }
                >>>     }
                >>>]
            parse_all: if True, will call parse_args otherwise calls parse_known_args
        """
        super().__init__()
        for arg_n in arg_list:
            args = arg_n.get('names', [])
            other_items = arg_n.get('other', {})
            self.add_argument(*args, **other_items)
        self.args = None
        self.arg_dict = {}
        if parse_all:
            self.parse = self.parse_args
        else:
            self.parse = self.parse_known_args
        self._process_args()

    def _process_args(self):
        """Processes args when using parse_known_args"""
        self.args = self.parse()
        if isinstance(self.args, tuple):
            for arg in self.args:
                if isinstance(arg, argparse.Namespace):
                    # Parse into dict and update
                    self.arg_dict.update(vars(arg))
        else:
            # Hopefully is already Namespace
            self.arg_dict = vars(self.args)


class LogArgParser:
    """Simple class for carrying over standard argparse routines to set log level"""
    def __init__(self, is_debugging: bool = False):
        self.log_level_str = 'INFO'    # Default
        args = [
            {
                'names': ['-lvl', '--level'],
                'other': {
                    'action': 'store',
                    'default': self.log_level_str
                }
            }
        ]
        self.ap = ArgParse(args, parse_all=False)
        if is_debugging:
            print('Bypassing argument parser in test environment')
            self.log_level_str = 'DEBUG'
        else:
            # Not running tests in PyCharm, so take in args
            arg_dict = self.ap.arg_dict
            self.log_level_str = arg_dict.get('level', self.log_level_str)


class Log:
    """Initiates a logging object to record processes and errors"""

    def __init__(self, log: Union[str, 'Log'] = None, child_name: str = None, log_level_str: str = None,
                 log_to_file: bool = True, log_dir: str = None):
        """
        Args:
            log: display name of the log. If Log object, will extract name from that.
                Typically, this second method is done in the name of assigning a child log a parent.
                If NoneType, will use __name__.
            child_name: str, name of the child log.
                This is used when the log being made is considered a child to the parent log name
            log_to_file: if True, will create a file handler for outputting logs to file.
                The files are incremented in days, with the date appended to the file name.
                Logs older than 20 days will be removed upon instantiation
            log_level_str: str, minimum logging level to write to log (Levels: DEBUG -> INFO -> WARN -> ERROR)
                default: 'INFO'
            log_dir: str, directory to save the log
                default: "~/logs/{log_name}/"
        """
        # If 'Log', it's a parent Log instance. Take the name from the object. Otherwise it's just a string
        if log is None:
            log = __name__
        self.log_name = log.log_name if isinstance(log, Log) else log
        # Determine if log is child of other Log objects (if so, it will be attached to that parent log)
        self.is_child = child_name is not None
        self.parent = log if self.is_child else None

        # Instantiate the log object
        if self.is_child:
            # Attach this instance to the parent log
            self.logger = logging.getLogger(self.log_name).getChild(child_name)
        else:
            # Create logger if it hasn't been created
            self.logger = logging.getLogger(self.log_name)

        # Check if debugging in pycharm
        # Checking Methods:
        #   1) checks for whether code run in-console
        #   2) check for script run in debug mode per PyCharm
        sysargs = sys.argv
        self.is_debugging = any(['pydevconsole.py' in sysargs[0], sys.gettrace() is not None])
        # Set the log level (will automatically set to DEBUG if is_debugging)
        self._set_log_level(log_level_str)

        # Set the log handlers
        if not self.is_child:
            # Create file handler for log (children of the object will simply inherit this)
            if log_to_file:
                self._build_log_path(log_dir)
            self._set_handlers(log_to_file)
        self.info(f'Logging initiated{" for child instance" if self.is_child else ""}.')

    def _build_log_path(self, log_dir: str):
        """Builds a filepath to the log file"""
        # Set name of file
        self.log_filename = f"{self.log_name}"
        # Set log directory (if none)
        home_dir = os.path.join(os.path.expanduser('~'), 'logs')
        log_dir = os.path.join(home_dir, log_dir if log_dir is not None else self.log_name)
        # Check if logging directory exists
        if not os.path.exists(log_dir):
            # If dir doesn't exist, create
            os.makedirs(log_dir)

        # Path of logfile
        self.log_path = os.path.join(log_dir, self.log_filename)

    def _set_log_level(self, log_level_str: str):
        # Get minimum log level to record (Structure goes: DEBUG -> INFO -> WARN -> ERROR)
        if log_level_str is None:
            if self.is_child:
                log_level_str = logging.getLevelName(self.parent.log_level_int) \
                    if isinstance(self.parent, Log) else 'INFO'
            else:
                # No log level provided. Check if any included as cmd argument
                log_level_str = LogArgParser(self.is_debugging).log_level_str
        self.log_level_str = log_level_str
        self.log_level_int = getattr(logging, log_level_str.upper(), logging.DEBUG)
        # Set minimum logging level
        self.logger.setLevel(self.log_level_int)

    def _set_handlers(self, log_to_file: bool):
        """Sets up file & stream handlers"""
        # Set format of logs
        formatter = logging.Formatter('%(asctime)s - %(name)s_%(process)d - %(levelname)-8s %(message)s')
        # Create streamhandler for log (this sends streams to stdout/stderr for debug help)
        sh = logging.StreamHandler()
        sh.setLevel(self.log_level_int)
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)

        if log_to_file and not self.is_debugging:
            # TimedRotating will delete logs older than 30 days
            # fh = TimedPatternFileHandler(self.log_path, when='M', backup_cnt=2)
            fh = TimedRotatingFileHandler(self.log_path, when='M', interval=1, backupCount=30)
            fh.setLevel(self.log_level_int)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        # Intercept exceptions
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type: type, exc_value: BaseException, exc_traceback: TracebackType):

        self._handle_exception(exc_type=exc_type, exc_value=exc_value, exc_traceback=exc_traceback)

    def _handle_exception(self, exc_type: type, exc_value: BaseException, exc_traceback: TracebackType):
        """Intercepts an exception and prints it to log file"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def info(self, text: str):
        """Info-level logging"""
        self.logger.info(text)

    def debug(self, text: str):
        """Debug-level logging"""
        self.logger.debug(text)

    def warning(self, text: str):
        """Warn-level logging"""
        self.logger.warning(text)

    def error(self, text: str, incl_info: bool = True):
        """Error-level logging"""
        self._error(text=text, incl_info=incl_info)

    def _error(self, text: str, incl_info: bool = True):
        """Error-level logging - private to allow for other log
         classes to inherit this plus their additional procedures"""
        self.logger.error(text, exc_info=incl_info)

    def error_from_class(self, err_obj: BaseException, text: str):
        """Error logging for exception objects"""
        self._error_from_class(err_obj=err_obj, text=text)

    def _error_from_class(self, err_obj: BaseException, text: str):
        """Error logging for exception objects"""
        traceback_msg = '\n'.join(traceback.format_tb(err_obj.__traceback__))
        exception_msg = f'{err_obj.__class__.__name__}: {err_obj}\n{traceback_msg}'
        err_msg = f'{text}\n{exception_msg}'
        self._error(err_msg)

    @staticmethod
    def extract_err() -> Tuple[Optional[type], Optional[BaseException], Optional[TracebackType]]:
        """Calls sys.exec_info() to get error details upon error instance
        Returns:
            (error type, error object, error traceback)
        """
        return sys.exc_info()

    def close(self):
        """Close logger"""
        disconn_msg = 'Log disconnected'
        if self.is_child:
            self.logger.info(f'{disconn_msg} for child instance.')
        else:
            self.logger.info(f'{disconn_msg}.\n' + '-' * 80)
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)


class LogWithInflux(Log):
    """Logging object that supports error logging to local Influxdb instance"""
    def __init__(self, log: Union[str, 'Log'], child_name: str = None, log_level_str: str = None,
                 log_to_file: bool = True, log_dir: str = None, log_to_db: bool = True):
        super().__init__(log=log, child_name=child_name, log_level_str=log_level_str, log_to_file=log_to_file,
                         log_dir=log_dir)
        self.log_to_db = log_to_db
        if self.is_debugging and self.log_to_db:
            self.debug('Debug mode activated. Disabling influx db logging.')

        if self.log_to_db and not self.is_debugging:
            # Only log errors if we're not debugging
            self.debug('Establishing connection to Influxdb.')
            self.machine = NetTools().get_hostname()
            # Set up influx object for logging errors
            self.influx = InfluxDBLocal(InfluxDBNames.HOMEAUTO)
        else:
            self.influx = None

        # Reset the exception hook
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type: type, exc_value: BaseException,
                         exc_traceback: TracebackType):
        self._handle_exception(exc_type=exc_type, exc_value=exc_value, exc_traceback=exc_traceback)
        # Log error to influxdb
        self._log_error_to_influx("Uncaught exception", exc_value)

    def error(self, text: str, incl_info: bool = True):
        self._error(text=text, incl_info=incl_info)
        # Try to grab the error object here, too
        err_type, err_obj, err_traceback = self.extract_err()
        # Log error to influxdb
        self._log_error_to_influx(text, err_obj)

    def error_from_class(self, err_obj: BaseException, text: str):
        self._error_from_class(err_obj=err_obj, text=text)
        # Log error to influxdb
        self._log_error_to_influx(text, err_obj)

    def _log_error_to_influx(self, text: str, err_obj: BaseException = None):
        """Logs an error to the database"""
        if self.log_to_db:
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
            self.influx.write_single_data(InfluxTblNames.LOGS,
                                          tag_dict=log_dict, field_dict=field_dict)
            self.debug('Logged error to influx.')
