#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .gpio import GPIO
import time


class Relay:
    """Relay stuff"""
    def __init__(self, pin):
        """
        Args:
            pin: int, BCM pin to relay
        """
        self.relay = GPIO(pin, mode='bcm', status='output')

    def turn_on(self, back_off_sec=0):
        """
        Turn relay to ON position
            NOTE: This is for the NC-type relay
        """
        self.relay.set_output(0)
        if back_off_sec > 0:
            time.sleep(back_off_sec)
            self.turn_off()

    def turn_off(self):
        """
        Turn relay to OFF position
            NOTE: This is for the NC-type relay
        """
        self.relay.set_output(1)

    def close(self):
        """Cleans up relay connection"""
        self.relay.cleanup()
