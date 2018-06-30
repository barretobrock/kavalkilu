#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .gpio import GPIO


class Relay:
    """Relay stuff"""
    def __init__(self, pin):
        """
        Args:
            pin: int, BCM pin to relay
        """
        self.relay = GPIO(pin, mode='bcm')

    def turn_on(self):
        """Turn relay to ON position"""
        self.relay.set_status(1)

    def turn_off(self):
        """Turn relay to OFF position"""
        self.relay.set_status(0)

    def toggle(self):
        """Toggle relay"""
        self.relay.set_status(not bool(self.relay.get_input()))

    def close(self):
        """Cleans up relay connection"""
        self.relay.cleanup()