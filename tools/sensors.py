#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .gpio import GPIO
import time
from importlib import import_module


class TempSensor:
    """
    Handle universal temperature sensor stuff
    """

    def __init__(self, d=2):
        self.decimals = d

    def round_reads(self, data):
        """
        Goes through data and rounds info to x decimal places
        Args:
            data: dict, temp/humidity data to round
                keys - 'humidity', 'temp'
        """
        # Loop through readings, remove any float issues by rounding off to 2 decimals
        for k, v in data.items():
            if isinstance(v, int):
                # Enforce float
                v = float(v)
            if isinstance(v, float):
                data[k] = round(v, self.decimals)
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
        self.dht = import_module('Adafruit_DHT')
        self.sensor = self.dht.DHT22
        self.pin = pin

    def measure(self):
        """Take a measurement"""
        humidity, temp = self.dht.read_retry(self.sensor, self.pin)
        readings = {
            'humidity': humidity,
            'temp': temp
        }
        # Loop through readings, remove any float issues by rounding off to 2 decimals
        readings = self.round_reads(readings)
        return readings


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


class PIRSensor:
    """
    Functions for a PIR motion sensor
    """
    def __init__(self, pin):
        """
        Args:
            pin: int, the BCM pin related to the PIR sensor
        """
        self.sensor = GPIO(pin, mode='bcm')

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



