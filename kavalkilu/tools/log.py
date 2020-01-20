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
from datetime import datetime as dt
from .path import Paths


class Log:
    """Initiates a logging object to record processes and errors"""

    def __init__(self, log_name, child_name=None, log_filename_prefix=None, log_dir=None, log_lvl='INFO'):
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
        # Name of log in logfile
        self.is_child = child_name is not None
        if self.is_child:
            # We've already had a logger set up, so find that and set this instance as a child of that instance
            self.logger = logging.getLogger(log_name).getChild(child_name)
        else:
            self.log_name = f'{log_name}_{dt.now():%H%M}'
            if log_filename_prefix is None:
                log_filename_prefix = log_name
            # Set name of file
            self.log_filename = f"{log_filename_prefix}_{dt.today():%Y%m%d}.log"
            # Set log directory (if none)
            if log_dir is None:
                log_dir = os.path.join(Paths().log_dir, log_name)
            # Check if logging directory exists
            if not os.path.exists(log_dir):
                # If dir doesn't exist, create
                os.makedirs(log_dir)

            # Path of logfile
            self.log_path = os.path.join(log_dir, self.log_filename)
            # Create logger if it hasn't been created
            self.logger = logging.getLogger(self.log_name)

        # Get minimum log level to record (Structure goes: DEBUG -> INFO -> WARN -> ERROR)
        self.logger_lvl = getattr(logging, log_lvl.upper(), logging.DEBUG)
        # Set minimum logging level
        self.logger.setLevel(self.logger_lvl)

        if not self.is_child:
            # Create file handler for log
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
        self.info(f'Logging initiated{" for child instance" if self.is_child else ""}.')

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Intercepts an exception and prints it to log file"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def info(self, text):
        """Info-level logging"""
        self.logger.info(text)

    def debug(self, text):
        """Debug-level logging"""
        self.logger.debug(text)

    def warning(self, text):
        """Warn-level logging"""
        self.logger.warning(text)

    def error(self, text):
        """Error-level logging"""
        self.logger.error(text, exc_info=True)

    def error_with_class(self, err_obj, text):
        """Error-level logging that also preserves the class of the error"""
        traceback_msg = '\n'.join(traceback.format_tb(err_obj.__traceback__))
        exception_msg = '{}: {}\n\n{}'.format(err_obj.__class__.__name__, err_obj, traceback_msg)
        err_msg = '{}\n{}'.format(exception_msg, text)
        self.logger.error(err_msg)

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


class LogArgParser:
    """Simple class for carrying over standard argparse routines to set log level"""
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-lvl', action='store', default='INFO')
        sysargs = sys.argv
        if 'pydevconsole.py' not in sysargs[0]:
            # Not running tests in PyCharm, so take in args
            self.args = self.parser.parse_args()
            self.loglvl = self.args.lvl.upper()
        else:
            print('Bypassing argument parser in test environment')
            self.loglvl = 'DEBUG'
