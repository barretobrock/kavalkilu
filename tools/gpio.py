#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as gpio


class GPIO:
    """
    Connects to GPIO on Raspberry Pi
    Args:
        pin: int, BCM pin on GPIO
        mode: str, what setup mode to run ('board', 'bcm')
        setwarn: bool, if True, allows GPIO warnings
    """

    def __init__(self, pin, mode='bcm', setwarn=False):
        self.GPIO = gpio
        self.pin = pin
        self.GPIO.setwarnings(setwarn)
        # Determine pin mode
        if mode == 'board':
            # BOARD
            self.GPIO.setmode(self.GPIO.BOARD)
        elif mode == 'bcm':
            # BCM
            # Use 'gpio readall' to get BCM pin layout for RasPi model
            self.GPIO.setmode(self.GPIO.BCM)

    def get_input(self, pin):
        """Reads value of pin"""
        return self.GPIO.input(pin)

    def set_status(self, pin, status):
        """
        Sets the pin status as on/HIGH(1) off/LOW(0)
            NOTE: Can pass tuples into status for quick succession changes
        """
        self.GPIO.output(pin, status)

    def cleanup(self, pin=None):
        """Resets GPIO by pin or for entire board"""
        if pin is None:
            self.GPIO.cleanup()
        else:
            self.GPIO.cleanup(pin)
