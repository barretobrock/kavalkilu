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
        status: str, whether to read info or send it (input, output)
        setwarn: bool, if True, allows GPIO warnings
        is_activelow: bool, if True, relay is off until setup. Delays setup until activation
    """

    def __init__(self, pin, mode='bcm', status='input', setwarn=False, is_activelow=False):
        self.GPIO = import_module('RPi.GPIO')
        self.pin = pin
        self.GPIO.setwarnings(setwarn)
        self.mode = mode
        self.status = status.lower()
        self.is_activelow = is_activelow

        # Set pin mode
        self.set_mode()
        if not self.is_activelow:
            # Set status if relay is not activelow
            self.set_status()

    def set_mode(self):
        if self.mode == 'board':
            # BOARD
            self.GPIO.setmode(self.GPIO.BOARD)
        elif self.mode == 'bcm':
            # BCM
            # Use 'gpio readall' to get BCM pin layout for RasPi model
            self.GPIO.setmode(self.GPIO.BCM)

    def set_status(self):
        """Sets the pin status as on/HIGH(1) off/LOW(0)"""
        if self.status == 'output':
            self.GPIO.setup(self.pin, self.GPIO.OUT)
        elif self.status == 'input':
            self.GPIO.setup(self.pin, self.GPIO.IN)

    def get_input(self):
        """Reads value of pin, only if the pin is set up for reading inputs"""
        if self.status == 'input':
            return self.GPIO.input(self.pin)
        else:
            # In case pin has been set up for output
            #   Can't read input when setup as output
            raise ValueError('Status for GPIO object is not "input"')

    def set_output(self, position):
        """Writes value (0,1) to pin"""
        if position not in [0, 1]:
            raise ValueError('Invalid position selected: (0, 1)')
        if self.status == 'output':
            self.GPIO.output(self.pin, position)
        else:
            raise ValueError('Status for GPIO object is not "output"')

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
