#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from typing import Union


class DateTools:
    def __init__(self):
        self.iso_date_fmt = '%Y-%m-%d'
        self.iso_datetime_fmt = f'{self.iso_date_fmt} %H:%M:%S'

    @staticmethod
    def last_day_of_month(any_day: datetime) -> datetime:
        """Retrieves the last day of the month for the given date"""
        next_month = any_day.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    @staticmethod
    def string_to_datetime(datestring: str, strftime_string: str = '%Y%m%d') -> datetime:
        """Converts string to datetime"""
        return datetime.strptime(datestring, strftime_string)

    @staticmethod
    def string_to_unix(date_string: str, strftime_string: str = '%Y%m%d') -> float:
        """Converts string to unix"""
        unix = (datetime.strptime(date_string, strftime_string) -
                datetime(1970, 1, 1)).total_seconds()
        return unix * 1000

    @staticmethod
    def unix_to_string(unix_date: float, output_fmt: str = '%Y-%m-%d') -> str:
        """Convert unix timestamp to string"""
        date_string = datetime.fromtimestamp(unix_date).strftime(output_fmt)
        return date_string

    def _tz_convert(self, from_tz: str, to_tz: str, obj: Union[datetime, str],
                    fmt: str = None) -> datetime:
        """Converts from one timezone to another using the dateutil library"""
        tz_from = tz.gettz(from_tz)
        tz_to = tz.gettz(to_tz)
        if isinstance(obj, str):
            if fmt is None:
                fmt = self.iso_datetime_fmt
            obj = datetime.strptime(obj, fmt)
        return obj.replace(tzinfo=tz_from).astimezone(tz_to)

    def local_time_to_utc(self, obj: Union[datetime, str], local_tz: str = 'US/Central',
                          fmt: str = None, as_str: bool = False) -> Union[datetime, str]:
        """Run if we're converting timestamps to UTC"""
        dt_obj = self._tz_convert(local_tz, 'UTC', obj, fmt)
        if as_str:
            return dt_obj.strftime('%F %T')
        else:
            return dt_obj

    def utc_to_local_time(self, obj: Union[datetime, str], local_tz: str = 'US/Central',
                          fmt: str = None, as_str: bool = False) -> Union[datetime, str]:
        """Run if we're converting timestamps to UTC"""
        dt_obj = self._tz_convert('UTC', local_tz, obj, fmt)
        if as_str:
            return dt_obj.strftime('%F %T')
        else:
            return dt_obj

    @staticmethod
    def seconds_since_midnight(timestamp: datetime) -> float:
        """Calculates the number of seconds since midnight"""
        seconds = (timestamp - timestamp.replace(hour=0, minute=0, second=0)).total_seconds()
        return seconds

    @staticmethod
    def human_readable(reldelta: timedelta) -> str:
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
