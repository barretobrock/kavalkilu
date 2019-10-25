#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common methods for error message & traceback extraction"""
import traceback


def format_exception(exc_obj, incl_traceback=False):
    """Takes in an exception object and parses out class, message and traceback (if desired)"""
    msg = '{}: {}'.format(exc_obj.__class__.__name__, exc_obj)
    if incl_traceback:
        msg = '{}\n{}'.format('\n'.join(traceback.format_tb(exc_obj.__traceback__)), msg)
    return msg
