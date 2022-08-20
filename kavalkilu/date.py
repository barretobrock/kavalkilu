#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from typing import Union

from dateutil import (
    relativedelta,
    tz,
)


class DateTools:
    TZ_UTC = tz.gettz('UTC')
    TZ_CT = tz.gettz('US/Central')
    ISO_DATE_STR = '%Y-%m-%d'
    ISO_DATETIME_STR = f'{ISO_DATE_STR} %H:%M:%S'

    @staticmethod
    def last_day_of_month(any_day: datetime) -> datetime:
        """Retrieves the last day of the month for the given date"""
        next_month = any_day.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    @classmethod
    def string_to_datetime(cls, datestring: str, strftime_string: str = None) -> datetime:
        """Converts string to datetime"""
        if strftime_string is None:
            strftime_string = cls.ISO_DATETIME_STR
        return datetime.strptime(datestring, strftime_string)

    @classmethod
    def dt_to_unix(cls, dt_obj: datetime, from_tz: tz.tzfile = TZ_CT) -> int:
        """Converts datetime object to unix"""
        unix_start = datetime(1970, 1, 1)
        if dt_obj.tzinfo is not None or from_tz is not None:
            # dt_obj is timezone-aware, so make UTC the same
            unix_start = unix_start.replace(tzinfo=cls.TZ_UTC)
        if from_tz is not None:
            dt_obj = dt_obj.replace(tzinfo=from_tz)

        return int((dt_obj - unix_start).total_seconds())

    @staticmethod
    def unix_to_dt(unix_ts: Union[float, int], to_tz: str = None) -> datetime:
        """Converts unix epoch to datetime"""
        if to_tz is not None:
            tz_obj = tz.gettz(to_tz)
            return datetime.fromtimestamp(unix_ts, tz=tz_obj)
        return datetime.fromtimestamp(unix_ts)

    @classmethod
    def string_to_unix(cls, date_string: str, strftime_string: str = None,
                       unit: str = 's', from_tz: Union[str, tz.tzfile] = TZ_CT) -> int:
        """Converts string to unix"""
        if strftime_string is None:
            strftime_string = cls.ISO_DATETIME_STR
        if isinstance(from_tz, str):
            from_tz = tz.gettz(from_tz)
        dt_obj = datetime.strptime(date_string, strftime_string)
        unix = cls.dt_to_unix(dt_obj, from_tz=from_tz)
        return unix * 1000 if unit == 'ms' else unix

    @classmethod
    def unix_to_string(cls, unix_ts: Union[float, int], output_fmt: str = None) -> str:
        """Convert unix timestamp to string"""
        if output_fmt is None:
            output_fmt = cls.ISO_DATETIME_STR
        return cls.unix_to_dt(unix_ts).strftime(output_fmt)

    @classmethod
    def _tz_convert(cls, from_tz: str, to_tz: str, obj: Union[datetime, str],
                    fmt: str = None) -> datetime:
        """Converts from one timezone to another using the dateutil library"""
        tz_from = tz.gettz(from_tz)
        tz_to = tz.gettz(to_tz)
        if isinstance(obj, str):
            if fmt is None:
                fmt = cls.ISO_DATETIME_STR
            obj = datetime.strptime(obj, fmt)
        return obj.replace(tzinfo=tz_from).astimezone(tz_to)

    @classmethod
    def local_time_to_utc(cls, obj: Union[datetime, str], local_tz: str = 'US/Central',
                          fmt: str = None, as_str: bool = False) -> Union[datetime, str]:
        """Run if we're converting timestamps to UTC"""
        dt_obj = cls._tz_convert(local_tz, 'UTC', obj, fmt)
        if as_str:
            return dt_obj.strftime('%F %T')
        else:
            return dt_obj

    @classmethod
    def utc_to_local_time(cls, obj: Union[datetime, str], local_tz: str = 'US/Central',
                          fmt: str = None, as_str: bool = False) -> Union[datetime, str]:
        """Run if we're converting timestamps to UTC"""
        dt_obj = cls._tz_convert('UTC', local_tz, obj, fmt)
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
    def _human_readable(reldelta: relativedelta) -> str:
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
                if attr_val > 0:
                    result_list.append('{:d}{}'.format(attr_val, attrs[attr]))
        return ' '.join(result_list)

    @classmethod
    def get_human_readable_date_diff(cls, start: datetime, end: datetime) -> str:
        """Outputs a breakdown of difference between the two dates from largest to smallest"""
        result = relativedelta.relativedelta(end, start)
        return cls._human_readable(result)
