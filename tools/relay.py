#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .gpio import GPIO
import time


class Relay:
    """Relay stuff"""
    def __init__(self, pin, is_activelow=True):
        """
        Args:
            pin: int, BCM pin to relay
            is_activelow: bool, if True, relay is off until setup. Delays setup until activation
        """
        self.is_activelow = is_activelow
        self.relay = GPIO(pin, mode='bcm', status='output', is_activelow=self.is_activelow)

    def turn_on(self, back_off_sec=0):
        """
        Turn relay to ON position
            NOTE: This is for the NC-type relay
        """
        if self.is_activelow:
            self.relay.set_mode()
            self.relay.set_status()
        else:
            self.relay.set_output(0)
        if back_off_sec > 0:
            time.sleep(back_off_sec)
            self.turn_off()

    def turn_off(self):
        """
        Turn relay to OFF position
            NOTE: This is for the NC-type relay
        """
        if self.is_activelow:
            self.relay.cleanup()
        else:
            self.relay.set_output(1)

    def close(self):
        """Cleans up relay connection"""
        self.relay.cleanup()
