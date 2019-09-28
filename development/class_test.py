#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse


class LogArgParser:
    """Simple class for carrying over standard argparse routines to set log level"""
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-lvl', action='store', default='INFO')
        self.args = self.parser.parse_args()
        self.loglvl = self.args.lvl