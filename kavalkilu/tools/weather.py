#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import List, Optional, Union
from collections import OrderedDict
from datetime import datetime as dtt
from datetime import timedelta
import pandas as pd
from meteocalc import feels_like, Temp, dew_point
from pyowm import OWM
from pyowm.weatherapi25.forecast import Forecast
from yr.libyr import Yr
from urllib.request import urlopen
from .net import Keys


# Locations for OWM
OWM_ATX = 'Austin,US'
OWM_TLL = 'Tallinn,EE'
OWM_RKV = 'Rakvere,EE'

# Some common locations for YrNo
YRNO_LOC_ATX = 'USA/Texas/Austin'
YRNO_LOC_TLL = 'Estonia/Harjumaa/Tallinn'
YRNO_LOC_RKV = 'Estonia/Lääne-Virumaa/Rakvere'

# NWS zones for alerts
NWS_ZONES_ATX = ['TXC453', 'TXZ192']


class OpenWeather:
    def __init__(self, location: str, tz: str = 'US/Central'):
        self.api_key = Keys().get_key('openweather_api')
        self.owm = OWM(self.api_key)
        self.location = location
        self.tz = tz

    def three_hour_summary(self) -> pd.DataFrame:
        """3h summary for the next 5 days"""
        data = self.owm.three_hours_forecast(self.location).get_forecast()
        return self._process_data(data, self.tz)

    def daily_summary(self) -> pd.DataFrame:
        """daily forecast for the next 5 days"""
        data = self.owm.daily_forecast(self.location, limit=5).get_forecast()
        return self._process_data(data, self.tz)

    @staticmethod
    def _process_data(data: Union[Forecast], tz: str) -> pd.DataFrame:
        cleaned = []
        for pt in data:
            temp = pt.get_temperature('celsius')['temp']
            wind = pt.get_wind('meters_sec')['speed']
            hum = pt.get_humidity()
            feels = feels_like(Temp(temp, 'c'), hum, wind).c
            dew_pt = pt.get_dewpoint() if pt.get_dewpoint() is not None else dew_point(temp, hum).c
            pt_dict = {
                'time': pd.to_datetime(pt.get_reference_time('iso')).tz_convert(tz),
                'summary': pt.get_detailed_status(),
                'precipIntensity': pt.get_rain()['3h'],
                'temperature': temp,
                'apparentTemperature': feels,
                'dewPoint': dew_pt,
                'humidity': hum / 100,
                'pressure': pt.get_pressure()['press'],
                'windSpeed': wind,
                'windBearing': pt.get_wind('meters_sec')['deg'],
                'cloudCover': pt.get_clouds() / 100,
                'visibility': pt.get_visibility_distance()
            }
            cleaned.append(pt_dict)
        return pd.DataFrame(cleaned)


class YrNoWeather:
    """Pulls weather data using Yr.no weather API"""
    def __init__(self, location: str, tz: str = 'US/Central'):
        """
        Args:
            location(str): location name `country/region/city`
            tz(str):  time zone to record time
        """
        self.location = location
        self.tz = tz

    @staticmethod
    def _process_data(data: dict) -> dict:
        """Process the raw data from YrNo API"""
        return {
            'from': pd.to_datetime(data['@from']),
            'to': pd.to_datetime(data['@to']),
            'summary': data['symbol']['@name'],
            'precipIntensity': float(data['precipitation']['@value']),
            'windBearing': float(data['windDirection']['@deg']),
            'windSpeed': float(data['windSpeed']['@mps']),
            'windSummary': data['windSpeed']['@name'],
            'temperature': float(data['temperature']['@value']),
            'pressure': float(data['pressure']['@value'])
        }

    def current_summary(self) -> pd.DataFrame:
        """Collect the current weather data for the location"""
        data = Yr(location_name=self.location).now()
        cleaned = pd.DataFrame(self._process_data(data), index=[1])
        return cleaned

    def hourly_summary(self) -> pd.DataFrame:
        """Creates a 48 hour forecast summary"""
        data = Yr(location_name=self.location, forecast_link='forecast_hour_by_hour')
        return pd.DataFrame([self._process_data(x) for x in data.forecast()])

    def daily_summary(self) -> pd.DataFrame:
        """Creates a 7-day forecast summary"""
        data = Yr(location_name=self.location)
        df = pd.DataFrame([self._process_data(x) for x in data.forecast()])
        # We'll need to group by day and have high/low calculated for each metric
        keep_cols = ['from', 'precipIntensity', 'windSpeed', 'temperature', 'pressure']
        df = df[keep_cols].groupby(pd.Grouper(key='from', freq='D')).agg(
            {x: ['min', 'max'] for x in keep_cols[1:]}
        )
        # Flatten the columns for the dataframe, but keep everything preserved from each level
        df.columns = ['_'.join(col).strip() for col in df.columns.values]
        return df


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
        k = Keys()
        self.DARK_SKY_API = k.get_key('darksky_api')
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
        time_cols = [col for col in df.columns if any([x in col.lower() for x in ['time', 'expire']])]
        df = self._convert_time_cols(time_cols, df)

        return df

    def _convert_time_cols(self, cols, df):
        """Converts time columns from epoch to local time"""
        if len(cols) > 0:
            for time_col in cols:
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

    def get_alerts(self):
        """Determines if there are any active weather alerts"""
        if 'alerts' not in self.data.keys():
            # No alerts
            return None
        alerts = self.data['alerts']
        df = self._format_tables(alerts)
        return df


class YrNoSelenium:
    """
    Collect data from YRNO via Selenium
    """
    def __init__(self):
        # Import selenium dependencies
        selenium_mod = __import__('kavalkilu.tools.selenium', fromlist=['ChromeDriver', 'BrowserAction'])
        BrowserAction = getattr(selenium_mod, 'BrowserAction')

        self.tomorrow = dtt.today() + timedelta(days=1)
        self.ba = BrowserAction()
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

    def hourly_forecast(self, city: str) -> Optional[List[dict]]:
        weather_list = []
        city_path = self.cities.get(city)
        if city_path is None:
            return None
        city_url = f"http://www.yr.no/place/{city_path}/hour_by_hour_detailed.html"
        self.ba.get(city_url)
        self.ba.fast_wait()
        # go through maximum four tables (there are usually just three)
        tbl_xpath = ''
        for x in range(1, 5):
            # xpath uses base 1 indexing!
            tbl_xpath = f'//table[@id="detaljert-tabell"][{x}]'
            date_text = self.ba.get_elem(f'{tbl_xpath}/caption[strong]')
            date = dtt.strptime(date_text.text.replace('Detailed forecast ', ''), '%B %d, %Y').date()
            if date.day == self.tomorrow.day:
                # found tomorrow's weather data
                break
        if date.day > 0:
            rows = self.ba.get_elem(f'{tbl_xpath}/tbody/tr', single=False)
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
                        timestamp_fix = [
                            (dtt.strptime(weather_list[p - 1].get('TIMESTAMP'), '%Y-%m-%d %H:%M:%S')
                             + timedelta(hours=hrs_all[k] - hrs[p - 1])).strftime('%Y-%m-%d %H:%M:%S')]
                        fix_dict = weather_list[p - 1]
                        fix_dict['TIMESTAMP'] = timestamp_fix
                        weather_list_fix.append(fix_dict)
                weather_list = weather_list_fix
        return weather_list
