#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .gpio import GPIO
import time
import pandas as pd
from importlib import import_module
from .databases import MySQLLocal
from .openhab import OpenHab


class TempSensor:
    """
    Handle universal temperature sensor stuff
    """

    def __init__(self, d=2):
        self.decimals = d
        self.sensor_type = 'TEMP'

    def round_reads(self, data):
        """
        Goes through data and rounds info to x decimal places
        Args:
            data: dict, temp/humidity data to round
                keys - 'humidity', 'temp'
        """
        def rounder(value):
            """Rounds the value"""
            if isinstance(value, int):
                value = float(value)
            if isinstance(value, float):
                value = round(value, self.decimals)
            return value

        # Loop through readings, remove any float issues by rounding off to 2 decimals
        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = rounder(v)
        elif isinstance(data, (int, float)):
            data = rounder(data)
        return data


class DHTTempSensor(TempSensor):
    """
    DHT Temperature sensor
    """
    def __init__(self, pin, decimals=2):
        """
        Args:
            pin: int, BCM pin number for data pin to DHT sensor
        """
        TempSensor.__init__(self, d=decimals)
        self.sensor_model = 'DHT22'
        self.dht = import_module('Adafruit_DHT')
        self.sensor = self.dht.DHT22
        self.pin = pin

    def measure(self, n_times=1, sleep_between_secs=1):
        """Take a measurement"""

        measurement = {
            'humidity': [],
            'temp': []
        }
        for i in range(0, n_times):
            humidity, temp = self.dht.read_retry(self.sensor, self.pin)
            if all([x is not None for x in [temp, humidity]]):
                if humidity < 110:
                    # Make sure the humidity measurement is within bounds
                    measurement['humidity'].append(humidity)
                measurement['temp'].append(temp)
            time.sleep(sleep_between_secs)

        # Take average of the measurements
        for key, val in measurement.items():
            if len(val) > 0:
                # Calculate the average
                measurement[key] = sum(val) / len(val)
            else:
                measurement[key] = None

        return self.round_reads(measurement)


class DallasTempSensor(TempSensor):
    """
    Dallas-type temperature sensor
    """
    def __init__(self, serial):
        """
        Args:
            serial: str, the serial number for the temperature sensor.
                NOTE: found in /sys/bus/w1/devices/{}/w1_slave
        """
        TempSensor.__init__(self)
        self.sensor_model = 'DALLAS'
        self.sensor_path = '/sys/bus/w1/devices/{}/w1_slave'.format(serial)

    def measure(self):
        with open(self.sensor_path) as f:
            result = f.read()
        result_list = result.split('\n')
        for r in result_list:
            # Loop through line breaks and find temp line
            if 't=' in r:
                temp = float(r[r.index('t=') + 2:]) / 1000
                break
        reading = {
            'temp': self.round_reads(temp)
        }
        return reading


class DarkSkyWeatherSensor:
    """SensorWrapper for DarkSkyWeather"""

    def __init__(self, sensor):
        self.sensor = sensor
        self.sensor_model = 'DARKSKY'
        self.sensor_type = 'WEATHER'


class SensorLogger:
    """Unified method of recording sensor details"""

    def __init__(self, location, sensor):
        """
        Args:
            location: str, the location name of the sensor as it appears in homeautodb
            sensor: any *Sensor-type object
        """
        db_name = 'homeautodb'
        self.location = location
        self.sensor = sensor
        self.db_eng = MySQLLocal(db_name)
        self.qdict = {
            'db_name': db_name,
            'loc': location
        }
        self.loc_id, self.loc_openhab = self.lookup_location()
        self.readings = self.collect_readings()

    def lookup_location(self):
        """Given the name of the sensor, look up the location id"""
        lookup_query = """
        SELECT
            loc.id
            , loc.location
            , loc.openhab_name
        FROM
            {db_name}.locations AS loc
        WHERE
            loc.location = '{loc}'
        """.format(**self.qdict)

        loc_df = self._read_query(lookup_query)
        if not loc_df.empty:
            loc_id = loc_df['id'].values[0]
            loc_openhab = loc_df['openhab_name'].values[0]
        else:
            raise ValueError('Location "{loc}" was not found in the database.'.format(**self.qdict))
        return loc_id, loc_openhab

    def collect_readings(self):
        """Take sensor measurements"""
        now = pd.datetime.now()
        reading_ts = now.strftime('%Y-%m-%d %H:%M:%S')
        result_dict = {'timestamp': reading_ts}
        if self.sensor.sensor_type == 'TEMP':
            if self.sensor.sensor_model == 'DHT22':
                # We'll be collecting temperature & humidity
                avg_reading = self.sensor.measure(n_times=5)
                temp_avg, hum_avg = (avg_reading[k] for k in ['temp', 'humidity'])
                result_dict.update({
                    'temp': temp_avg,
                    'humidity': hum_avg
                })
            elif self.sensor.sensor_model == 'DALLAS':
                # Collecting only temperature
                result_dict.update(self.sensor.measure())
        elif self.sensor.sensor_model == 'DARKSKY':
            # Read in current readings
            cur_df = self.sensor.current_summary()
            # Build out a list of dataframes for each measurement to record
            cur_df['loc_id'] = self.loc_id
            cur_df['humidity'] = cur_df['humidity'] * 100
            # Convert to dict, flatten results
            result_dict.update({k: v[0] for k, v in cur_df.to_dict().items()})

        return result_dict

    def update(self, openhab=True, mysql=True):
        """Updates mysql db and openhab with sensor details
        """

        if openhab:
            # Update the OpenHab values
            self._update_openhab()
        if mysql:
            # Update the MySQL tables
            self._update_mysql()

    def _update_mysql(self):
        """Handles updating the MySQL db"""
        values_list = None
        if self.sensor.sensor_type == 'TEMP':
            if self.sensor.sensor_model == 'DHT22':
                # We'll be collecting temperature & humidity
                tables = ['temps', 'humidity']
                val_types = ['temp', 'humidity']
            elif self.sensor.sensor_model == 'DALLAS':
                # Just collecting temperature
                tables = ['temps']
                val_types = ['temp']
            else:
                raise ValueError('Unexpected temp sensor model: {}'.format(self.sensor.sensor_model))
        elif self.sensor.sensor_model == 'DARKSKY':
            tables = ['temps', 'humidity', 'ozone', 'wind', 'pressure']
            val_types = ['temperature', 'humidity', 'ozone', 'windSpeed', 'pressure']

        # build out a list of dictionary object of the values we're sending in
        values_list = [
            {
                'loc_id': self.loc_id,
                'record_date': self.readings['timestamp'],
                'record_value': self.readings[x],
                'tbl': y
            } for x, y in zip(val_types, tables)
        ]

        if values_list is not None:
            for vdict in values_list:
                # Insert into tables
                tbl = vdict.pop('tbl')
                df = pd.DataFrame(vdict, index=[0])
                self.db_eng.write_dataframe(tbl, df)

    def _update_openhab(self):
        """Handles updating openhab info"""
        oh = OpenHab()
        oh_values = None

        if self.sensor.sensor_type == 'TEMP':
            if self.sensor.sensor_model == 'DHT22':
                oh_values = {
                    'Env_{}_Update'.format(self.loc_openhab): self.readings['timestamp'],
                    'Temp_{}'.format(self.loc_openhab): self.readings['temp'],
                    'Hum_{}'.format(self.loc_openhab): self.readings['humidity']
                }
            elif self.sensor.sensor_model == 'DALLAS':
                oh_values = {
                    'Temp_{}'.format(self.loc_openhab): self.readings['temp'],
                }

        if oh_values is not None:
            for name, val in oh_values.items():
                req = oh.update_value(name, '{}'.format(val))

    def _read_query(self, query):
        """Gathers results for the given query"""
        res = pd.read_sql_query(query, self.db_eng.connection)
        return res


class PIRSensor:
    """
    Functions for a PIR motion sensor
    """
    def __init__(self, pin):
        """
        Args:
            pin: int, the BCM pin related to the PIR sensor
        """
        self.sensor = GPIO(pin, mode='bcm', status='input')
        self.sensor_type = 'PIR'

    def arm(self, sleep_sec=0.1, duration_sec=300):
        """
        Primes the sensor for detecting motion.
            If motion detected, returns unix time
        Args:
            sleep_sec: float, seconds to sleep between checks
            duration_sec: int, seconds to run script before exit
        """
        # Get current time
        start_time = time.time()
        end_time = start_time + duration_sec

        while end_time > time.time():
            # Measure once
            m1 = self.sensor.get_input()
            # Pause
            time.sleep(sleep_sec)
            # Measure twice
            m2 = self.sensor.get_input()
            if all([m1 == 1, m2 == 1]):
                return time.time()
        return None


class DistanceSensor:
    """Functions for the HC-SR04 Ultrasonic range sensor"""
    def __init__(self, trigger, echo):
        self.sensor_type = 'ULTRASONIC'
        self.sensor_model = 'HC-SR04'
        # Set up the trigger
        self.trigger = GPIO(trigger, status='output')
        # Set up feedback
        self.echo = GPIO(echo, status='input')

    def measure(self, wait_time=2, pulse_time=0.00001, round_decs=2):
        """Take distance measurement in mm"""
        # Wait for sensor to settle
        self.trigger.set_output(0)
        time.sleep(wait_time)
        # Pulse trigger
        self.trigger.set_output(1)
        time.sleep(pulse_time)
        self.trigger.set_output(0)

        # Get feedback
        while self.echo.get_input() == 0:
            pulse_start = time.time()

        while self.echo.get_input() == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150 * 100
        distance = round(distance, round_decs)

        return distance

    def close(self):
        """Clean up the pins associated with the sensor"""
        self.echo.cleanup()
        self.trigger.cleanup()

    def __del__(self):
        """Cleanup on deletion"""
        self.close()