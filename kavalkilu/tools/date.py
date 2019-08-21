#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime


class DateTools:
    def __init__(self):
        pass

    def last_day_of_month(self, any_day):
        """Retrieves the last day of the month for the given date"""
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def string_to_datetime(self, datestring, strftime_string='%Y%m%d'):
        """Converts string to datetime"""
        return datetime.datetime.strptime(datestring, strftime_string)

    def string_to_unix(self, date_string, strftime_string='%Y%m%d'):
        """Converts string to unix"""
        unix = (datetime.datetime.strptime(date_string, strftime_string) - datetime.datetime(1970, 1, 1)).total_seconds()
        return unix * 1000

    def unix_to_string(self, unix_date, output_fmt='%Y-%m-%d'):
        """Convert unix timestamp to string"""
        date_string = datetime.datetime.fromtimestamp(unix_date).strftime(output_fmt)
        return date_string

    def seconds_since_midnight(self, timestamp):
        """Calculates the number of seconds since midnight"""
        seconds = (timestamp - timestamp.replace(hour=0, minute=0, second=0)).total_seconds()
        return seconds

    def human_readable(self, reldelta):
        """Takes in a relative delta and makes it human readable"""
        attrs = {
            'years': 'y',
            'months': 'm',
            'days': 'd',
            'hours': 'h',
            'minutes': 'mins',
            'seconds': 's'
        }

        result_list = []
        for attr in attrs.keys():
            attr_val = getattr(reldelta, attr)
            if attr_val is not None:
                if attr_val > 1:
                    result_list.append('{:d}{}'.format(attr_val, attrs[attr]))
        return ' '.join(result_list)
