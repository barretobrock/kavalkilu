#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime


class DateTools:
    def __init__(self):
        pass

    @staticmethod
    def last_day_of_month(any_day: datetime.datetime) -> datetime.datetime:
        """Retrieves the last day of the month for the given date"""
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    @staticmethod
    def string_to_datetime(datestring: str, strftime_string: str = '%Y%m%d') -> datetime.datetime:
        """Converts string to datetime"""
        return datetime.datetime.strptime(datestring, strftime_string)

    @staticmethod
    def string_to_unix(date_string: str, strftime_string: str = '%Y%m%d') -> float:
        """Converts string to unix"""
        unix = (datetime.datetime.strptime(date_string, strftime_string) -
                datetime.datetime(1970, 1, 1)).total_seconds()
        return unix * 1000

    @staticmethod
    def unix_to_string(unix_date: float, output_fmt: str = '%Y-%m-%d') -> str:
        """Convert unix timestamp to string"""
        date_string = datetime.datetime.fromtimestamp(unix_date).strftime(output_fmt)
        return date_string

    @staticmethod
    def seconds_since_midnight(timestamp: datetime.datetime) -> float:
        """Calculates the number of seconds since midnight"""
        seconds = (timestamp - timestamp.replace(hour=0, minute=0, second=0)).total_seconds()
        return seconds

    @staticmethod
    def human_readable(reldelta: datetime.timedelta) -> str:
        """Takes in a relative delta and makes it human readable"""
        attrs = {
            'years': 'y',
            'months': 'mo',
            'days': 'd',
            'hours': 'h',
            'minutes': 'm',
            'seconds': 's'
        }

        result_list = []
        for attr in attrs.keys():
            attr_val = getattr(reldelta, attr)
            if attr_val is not None:
                if attr_val > 1:
                    result_list.append('{:d}{}'.format(attr_val, attrs[attr]))
        return ' '.join(result_list)
