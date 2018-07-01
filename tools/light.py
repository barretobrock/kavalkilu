#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .gpio import GPIO
from .path import Paths
import time
from random import random
from phue import Bridge


class LED:
    """LED light functions"""
    def __init__(self, pin):
        """
        Args:
            pin: int, BCM pin to relay
        """
        self.relay = GPIO(pin, mode='bcm')

    def turn_on(self):
        """
        Turn LED ON
        """
        self.relay.set_status(1)

    def turn_off(self):
        """
        Turn LED OFF
        """
        self.relay.set_status(0)

    def blink(self, times, wait=0.1):
        """Blinks LED x times, waiting y seconds between"""
        for x in range(0, times):
            self.turn_on()
            time.sleep(wait)
            self.turn_off()


class HueBulb:
    """Commands for Philips Hue bulbs"""
    # Set path to bridge ip
    p = Paths()
    b_ip = p.huebridge_ip

    def __init__(self, light_id, bridge_ip=b_ip):
        """
        Args:
            light_id: str name of light to control
            bridge_ip: str, ip address to the Philips Hue bridge
        """
        self.bridge = Bridge(bridge_ip)
        # Bridge button may need to be pressed the first time this is used
        self.bridge.connect()
        self.api = self.bridge.get_api()
        self.light_obj = self.bridge.get_light_objects('name')[light_id]

    def turn_on(self):
        """Turns light on"""
        self.light_obj.on = True

    def turn_off(self):
        """Turns light off"""
        self.light_obj.on = False

    def get_status(self):
        """Determine if light is on/off"""
        return self.light_obj.on

    def blink(self, times, wait=0.5):
        """Blinks light x times, waiting y seconds between"""
        for x in range(0, times):
            self.turn_on()
            time.sleep(wait)
            self.turn_off()

    def brightness(self, level):
        """Set brightness to x%
        Args:
            level: float, the brightness level to set
        """
        if level > 1:
            # Set level to percentage
            level = level / 100

        self.light_obj.brightness = 254 * level

    def color(self, color_coord):
        """Set the color of the light with x,y coordinates (0-1)"""
        self.light_obj.xy(color_coord)

    def rand_color(self):
        """Sets random color"""
        self.color([random(), random()])

    def alert(self, single=True, flash_secs=10):
        """Puts light into alert mode (flashing)"""
        if single:
            self.light_obj.alert = 'select'
        else:
            self.light_obj.alert = 'lselect'
            end_time = time.time() + flash_secs
            while end_time > time.time():
                pass
                time.sleep(0.1)
            # Turn off flashing
            self.light_obj.alert = 'none'

