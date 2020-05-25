#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common methods for error message & traceback extraction"""
import traceback


def format_exception(exc_obj: Exception, incl_traceback: bool = False) -> str:
    """Takes in an exception object and parses out class, message and traceback (if desired)"""
    msg = f'{exc_obj.__class__.__name__}: {exc_obj}'
    if incl_traceback:
        tb = '\n'.join(traceback.format_tb(exc_obj.__traceback__))
        msg = f'{tb}\n{msg}'
    return msg
