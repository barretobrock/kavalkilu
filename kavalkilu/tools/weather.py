#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from collections import OrderedDict
from datetime import datetime as dtt
from datetime import timedelta
import pandas as pd
from urllib.request import urlopen
from kavalkilu.tools.selenium import ChromeDriver, Action
from kavalkilu.tools.path import Paths


class DarkSkyWeather:
    """
    Use Dark Sky API to get weather forecast
    Args for __init__:
        day_text: str, 'TODAY' or 'TOMORROW'
        latlong: str, format: "latitude,longitude"
    """
    def __init__(self, day_text, latlong='59.4049,24.6768'):
        self.day_text = day_text
        self.latlong = latlong
        self.url_prefix = 'https://api.darksky.net/forecast'
        p = Paths()
        self.DARK_SKY_API = p.key_dict['darksky_api']
        self.DARK_SKY_URL = "{}/{}/{}?units=si&exclude=flags".format(self.url_prefix, self.DARK_SKY_API, self.latlong)

    def get_data(self):
        """Returns weather data on given location"""
        # get weather forecast from dark sky api
        darksky = urlopen(self.DARK_SKY_URL).read().decode('utf-8')
        data = json.loads(darksky)
        return data

    def day_summary(self, hour_list=None):
        """
        Creates summary of day's weather for location
        Args:
            hour_list: list of hours of day for specific temperatures
                If None, will return next 6 hours
        """
        now = dtt.today()
        data = self.get_data()
        hourly_weather = data.get('hourly').get('data')
        times = [dtt.fromtimestamp(int(x.get('time'))).strftime('%Y%m%d %H') for x in hourly_weather]

        if hour_list is None:
            hour_list = pd.date_range(now, (now + timedelta(hours=6)), freq='H')
        # determine when to get weather info
        num_days = 0
        if self.day_text == 'TODAY':
            num_days = 0
        elif self.day_text == 'TOMORROW':
            num_days = 1
        date_str = (now + timedelta(days=num_days)).strftime('%Y%m%d')
        text_list = []
        if len(hour_str_list) > 0:
            for i in hour_str_list:
                try:
                    ts = times.index("{} {}".format(date_str, i))
                    sumry = hourly_weather[ts].get('summary')
                    temp = round(float(hourly_weather[ts].get('temperature')), 1)
                    apptemp = round(float(hourly_weather[ts].get('apparentTemperature')), 1)
                    precip = float(hourly_weather[ts].get('precipIntensity'))
                    forecast_txt = "{}.00: {} (feels {}) {}".format(i, temp, apptemp, sumry)
                    if precip > 0.09:
                        forecast_txt += ' {precip}\n'
                    else:
                        forecast_txt += '\n'
                    text_list.append(forecast_txt)
                except:
                    pass
        text_list = [self.day_text + ':\n'] + text_list
        return ''.join(text_list)


class YrNoWeather:
    """
    Collect data from YRNO
    """
    def __init__(self):
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








