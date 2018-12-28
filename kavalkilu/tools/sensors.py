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
        self.dht = import_module('Adafruit_DHT')
        self.sensor = self.dht.DHT22
        self.pin = pin

    def measure(self, n_times=1, sleep_between_secs=1):
        """Take a measurement"""

        total_readings = []
        for i in range(0, n_times):
            humidity, temp = self.dht.read_retry(self.sensor, self.pin)
            # Loop through readings, remove any float issues by rounding off to 2 decimals
            reading = self.round_reads({
                'humidity': humidity,
                'temp': temp
            })
            total_readings.append(reading)
            time.sleep(sleep_between_secs)
        # Get average of all readings
        readings = {k: sum(x[k] for x in total_readings) / len(total_readings) for k in ['temp', 'humidity']}

        return self.round_reads(readings)


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
        self.sensor = GPIO(pin, mode='bcm', status='input')

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
