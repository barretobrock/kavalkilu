#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from collections import OrderedDict
from datetime import datetime as dtt
from datetime import timedelta
import pandas as pd
from urllib.request import urlopen
from .path import Paths


class DarkSkyWeather:
    """
    Use Dark Sky API to get weather forecast
    Args for __init__:
        latlong: str, format: "latitude,longitude"
    """
    def __init__(self, latlong='59.4049,24.6768', tz='US/Central'):
        self.latlong = latlong
        self.tz = tz
        self.url_prefix = 'https://api.darksky.net/forecast'
        p = Paths()
        self.DARK_SKY_API = p.key_dict['darksky_api']
        self.DARK_SKY_URL = "{}/{}/{}?units=si&exclude=flags".format(self.url_prefix, self.DARK_SKY_API, self.latlong)
        self.data = self._get_data()

    def _get_data(self):
        """Returns weather data on given location"""
        # get weather forecast from dark sky api
        darksky = urlopen(self.DARK_SKY_URL).read().decode('utf-8')
        data = json.loads(darksky)
        return data

    def _format_tables(self, data):
        """Takes in a grouping of data and returns as a pandas dataframe"""
        if isinstance(data, list):
            # Dealing with multiple rows of data
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Dealing with a single row of data
            df = pd.DataFrame(data, index=[0])

        # Convert any "time" column to locally-formatted datetime
        time_cols = [col for col in df.columns if 'time' in col.lower()]
        if len(time_cols) > 0:
            for time_col in time_cols:
                # Convert column to datetime
                dtt_col = pd.to_datetime(df[time_col], unit='s')
                # Convert datetime col to local timezone and remove tz
                dtt_col = dtt_col.dt.tz_localize('utc').dt.tz_convert(self.tz).dt.tz_localize(None)
                df[time_col] = dtt_col

        return df

    def current_summary(self):
        """Get current weather summary"""
        data = self.data['currently']
        df = self._format_tables(data)
        return df

    def hourly_summary(self):
        """Get 48 hour weather forecast"""
        data = self.data['hourly']['data']
        df = self._format_tables(data)
        return df

    def daily_summary(self):
        """Get 7-day weather forecast"""
        data = self.data['daily']['data']
        df = self._format_tables(data)
        return df


class YrNoWeather:
    """
    Collect data from YRNO
    """
    def __init__(self):
        # Import selenium dependencies
        selenium_mod = __import__('kavalkilu.tools.selenium', fromlist=['ChromeDriver', 'Action'])
        ChromeDriver = getattr(selenium_mod, 'ChromeDriver')
        Action = getattr(selenium_mod, 'Action')

        self.tomorrow = dtt.today() + timedelta(days=1)
        self.p = Paths()
        self.chrome_driver = self.p.chrome_driver
        self.b = ChromeDriver(self.chrome_driver).initiate()
        self.act = Action(self.b)
        self.cities = OrderedDict((
            ('Tallinn', 'Estonia/Harjumaa/Tallinn'),
            ('Kärdla', 'Estonia/Hiiumaa/Kärdla'),
            ('Jõhvi', 'Estonia/Ida-Virumaa/Jõhvi'),
            ('Jõgeva', 'Estonia/Jõgevamaa/Jõgeva'),
            ('Paide', 'Estonia/Järvamaa/Paide'),
            ('Haapsalu', 'Estonia/Läänemaa/Haapsalu'),
            ('Rakvere', 'Estonia/Lääne-Virumaa/Rakvere'),
            ('Põlva', 'Estonia/Põlvamaa/Põlva'),
            ('Rapla', 'Estonia/Raplamaa/Rapla'),
            ('Kuressaare', 'Estonia/Saaremaa/Kuressaare'),
            ('Tartu', 'Estonia/Tartumaa/Tartu'),
            ('Valga', 'Estonia/Valgamaa/Valga'),
            ('Viljandi', 'Estonia/Viljandimaa/Viljandi'),
            ('Võru', 'Estonia/Võrumaa/Võru')
        ))

    def hourly_forecast(self, city):
        weather_list = []
        city_path = self.cities.get(city)
        if city_path is None:
            return None
        city_url = "http://www.yr.no/place/{}/hour_by_hour_detailed.html".format(city_path)
        self.b.get(city_url)
        self.act.rand_wait('fast')
        # go through maximum four tables (there are usually just three)
        tbl_xpath = ''
        for x in range(1, 5):
            # xpath uses base 1 indexing!
            tbl_xpath = '//table[@id="detaljert-tabell"][{}]'.format(x)
            date_text = self.act.get(tbl_xpath + '/caption[strong]')
            date = dtt.strptime(date_text.text.replace('Detailed forecast ', ''), '%B %d, %Y').date()
            if date.day == self.tomorrow.day:
                # found tomorrow's weather data
                break
        if date.day > 0:
            rows = self.act.get(tbl_xpath + '/tbody/tr', single=False)
            for row in rows:
                hour = (dtt.strptime(row.find_element_by_xpath('th').text, '%H:%M') - timedelta(hours=1)).time()
                cols = row.find_elements_by_xpath('td')
                # combine date and time to form timestamp
                ts = dtt.combine(date, hour)
                weather_dict = OrderedDict((
                    ('TIMESTAMP', ts.strftime('%Y-%m-%d %H:%M:%S')),
                    ('CITY', city),
                    ('CONDITIONS', cols[0].get_attribute('title')[:cols[0].get_attribute('title').index('.')]),
                    ('TEMPERATURE', cols[1].text.replace('°', '')),
                    ('PRECIPITATION', cols[2].text.replace(' mm', '')),
                    ('WIND', cols[3].text[cols[3].text.index(',') + 2:cols[3].text.index('m/s') - 1]),
                    ('PRESSURE', cols[4].text.replace(' hPa', '')),
                    ('HUMIDITY', cols[5].text.replace(' %', '')),
                    ('DEW POINT', cols[6].text.replace('°', '')),
                    ('TOTAL CLOUD COVER', cols[7].text.replace(' %', '')),
                    ('FOG COVER', cols[8].text.replace(' %', '')),
                    ('LOW CLOUD COVER', cols[9].text.replace(' %', '')),
                    ('MIDDLE CLOUD COVER', cols[10].text.replace(' %', '')),
                    ('HIGH CLOUD COVER', cols[11].text.replace(' %', ''))
                ))
                weather_list.append(weather_dict)
            if len(weather_list) != 24:
                # if not all 24 hours are accounted for, divide the data into 24 hours
                # get list of existing hours first
                timestamps = [w.get('TIMESTAMP') for w in weather_list]
                hrs = [dtt.strptime(ts, '%Y-%m-%d %H:%M:%S').hour for ts in timestamps]
                hrs = hrs + [0] # added to keep ends from throwing index error
                hrs_all = [n for n in range(0, 24)]
                weather_list_fix = []
                p = 0
                for k in range(0, 24):
                    if hrs[p] == hrs_all[k]:
                        weather_list_fix.append(weather_list[p])
                        p += 1
                    else:
                        timestamp_fix = [(dtt.strptime(weather_list[p - 1].get('TIMESTAMP'), '%Y-%m-%d %H:%M:%S') + timedelta(hours=hrs_all[k] - hrs[p - 1])).strftime('%Y-%m-%d %H:%M:%S')]
                        fix_dict = weather_list[p - 1]
                        fix_dict['TIMESTAMP'] = timestamp_fix
                        weather_list_fix.append(fix_dict)
                weather_list = weather_list_fix
        return weather_list








