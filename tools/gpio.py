#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from importlib import import_module


class GPIO:
    """
    Connects to GPIO on Raspberry Pi
    Args:
        pin: int, BCM pin on GPIO
        mode: str, what setup mode to run ('board', 'bcm')
        setwarn: bool, if True, allows GPIO warnings
    """

    def __init__(self, pin, mode='bcm', setwarn=False):
        self.GPIO = import_module('RPi.GPIO')
        self.pin = pin
        self.GPIO.setwarnings(setwarn)
        self.status = 'Unset'
        # Determine pin mode
        if mode == 'board':
            # BOARD
            self.GPIO.setmode(self.GPIO.BOARD)
        elif mode == 'bcm':
            # BCM
            # Use 'gpio readall' to get BCM pin layout for RasPi model
            self.GPIO.setmode(self.GPIO.BCM)

    def get_input(self):
        """Reads value of pin, only if the pin is set up for reading inputs"""
        # For first-time setting
        if self.status == 'Unset':
            self.status = 'Input'
            self.GPIO.setup(self.pin, self.GPIO.IN)

        if self.status == 'Input':
            return self.GPIO.input(self.pin)
        else:
            # In case pin has been set up for output
            #   Can't read input when setup as output
            return None

    def set_status(self, status):
        """
        Sets the pin status as on/HIGH(1) off/LOW(0)
            NOTE: Can pass tuples into status for quick succession changes
        """
        if self.status == 'Unset':
            self.status = 'Output'
            self.GPIO.setup(self.pin, self.GPIO.OUT)

        if self.status == 'Output':
            self.GPIO.output(self.pin, status)

    def wait_for_action(self, action='rising', timeout=5000):
        """
        Blocks execution of program until an edge (change in state) is detected
        Args:
            action: str, the action (edge type) to wait for (rising, falling, both)
            timeout: int, wait time in milliseconds before stopping edge detect
        Examples:
            result = wait_for_action('falling')
            if result is None:
                print('Timeout! Nothing happened')
            else:
                print('Edge detected!')
        """
        if action == 'rising':
            edge = self.GPIO.RISING
        elif action == 'falling':
            edge = self.GPIO.FALLING
        elif action == 'both':
            edge = self.GPIO.BOTH

        return self.GPIO.wait_for_edge(self.pin, edge, timeout=timeout)

    def cleanup(self):
        """Resets GPIO by pin"""
        self.GPIO.cleanup(self.pin)
