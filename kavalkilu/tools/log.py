#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General log setup file.
"""
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime as dt


class Log:
    """
    Initiates an object to log processes from error-level to debug-level
    Args from __init__:
        log_name: str, display name of the log
        log_filename_prefix: str, filename prefix (ex. 'npslog')
            default: log_name
        log_dir: str, directory to save the log
            default: "~/logs"
        log_lvl: str, minimum logging level to write to log (Hierarchy: DEBUG -> INFO -> WARN -> ERROR)
            default: 'INFO'
    """
    def __init__(self, log_name, log_filename_prefix=None, log_dir=None, log_lvl='INFO'):
        # Name of log in logfile
        self.log_name = log_name
        if log_filename_prefix is None:
            log_filename_prefix = log_name
        # Set name of file
        self.log_filename = "{}_{}.log".format(log_filename_prefix, dt.today().strftime('%Y%m%d'))
        # Set log directory (if none)
        if log_dir is None:
            log_dir = os.path.join(os.path.expanduser('~'), 'logs')
        # Check if logging directory exists
        if not os.path.exists(log_dir):
            # If doesn't exist, create
            try:
                os.makedirs(log_dir)
            except:
                pass

        # Path of logfile
        self.log_path = os.path.join(log_dir, self.log_filename)
        # Create logger
        self.logger = logging.getLogger(self.log_name)
        # Get minimum log level to record (Structure goes: DEBUG -> INFO -> WARN -> ERROR)
        self.logger_lvl = getattr(logging, log_lvl.upper(), logging.DEBUG)
        # Set minimum logging level
        self.logger.setLevel(self.logger_lvl)
        # create file handler for log
        # TimedRotating will delete logs older than 30 days
        fh = TimedRotatingFileHandler(self.log_path, when='d', interval=1, backupCount=30)
        # fh = logging.FileHandler(self.log_path)
        fh.setLevel(logging.DEBUG)
        # create streamhandler for log
        sh = logging.StreamHandler()
        sh.setLevel(logging.WARNING)
        # set format of logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s %(message)s')
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)
        # add handlers to log
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)
        sys.excepthook = self.handle_exception

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
        self.logger.debug('Log disconnected.\n' + '-' * 80)
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

