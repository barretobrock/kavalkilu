#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from kavalkilu.tools.relay import Relay

# Pin to relay 1 (take BCM pin from 'gpio readall' command)
PIN = 23

# Set up garage relay
gr = Relay(PIN)

# Activate door
gr.turn_on()
time.sleep(1)
gr.turn_off()

# Cleanup pin
gr.close()