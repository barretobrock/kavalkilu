#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General log setup file.
"""
import os
import sys
import logging
import argparse
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime as dt


class Log:
    """Initiates a logging object to record processes and errors"""

    def __init__(self, log_name, log_filename_prefix=None, log_dir=None, log_lvl='INFO'):
        """
        Args:
            log_name: str, display name of the log. Will have the time (H:M) added to the end
                to denote separate instances)
            log_filename_prefix: str, filename prefix (ex. 'npslog')
                default: log_name
            log_dir: str, directory to save the log
                default: "~/logs"
            log_lvl: str, minimum logging level to write to log (Hierarchy: DEBUG -> INFO -> WARN -> ERROR)
                default: 'INFO'
        """
        # Name of log in logfile
        self.log_name = '{}_{:%H%M}'.format(log_name, dt.now())
        if log_filename_prefix is None:
            log_filename_prefix = log_name
        # Set name of file
        self.log_filename = "{}_{}.log".format(log_filename_prefix, dt.today().strftime('%Y%m%d'))
        # Set log directory (if none)
        if log_dir is None:
            log_dir = os.path.join(os.path.expanduser('~'), *['logs', log_filename_prefix])
        # Check if logging directory exists
        if not os.path.exists(log_dir):
            # If dir doesn't exist, create
            os.makedirs(log_dir)

        # Path of logfile
        self.log_path = os.path.join(log_dir, self.log_filename)
        # Create logger
        self.logger = logging.getLogger(self.log_name)
        # Get minimum log level to record (Structure goes: DEBUG -> INFO -> WARN -> ERROR)
        self.logger_lvl = getattr(logging, log_lvl.upper(), logging.DEBUG)
        # Set minimum logging level
        self.logger.setLevel(self.logger_lvl)
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
        self.info('Logging initiated.')

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
        self.logger.error(text)

    def close(self):
        """Close logger"""
        self.logger.info('Log disconnected.\n' + '-' * 80)
        handlers = self.logger.handlers
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def __del__(self):
        """In case logger hasn't been properly closed"""
        try:
            self.close()
        except:
            pass


class LogArgParser:
    """Simple class for carrying over standard argparse routines to set log level"""
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-lvl', action='store', default='INFO')
        sysargs = sys.argv
        if 'pydevconsole.py' not in sysargs[0]:
            self.args = self.parser.parse_args()
            self.loglvl = self.args.lvl.upper()
        else:
            print('Bypassing argument parser in test environment')
            self.loglvl = 'DEBUG'
