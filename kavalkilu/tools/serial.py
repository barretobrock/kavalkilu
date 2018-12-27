#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read in data from serial bus"""

import serial # Installed by apt-get install python3-serial

usb_interface_name = '/dev/ttyUSB1'

ser = serial.Serial(usb_interface_name, 9600)

try:
    while 1:
        t = ser.readline()
        print(t)
except KeyboardInterrupt:
    ser.close()

# Clean serial output
clean_str = str(t)[2:-5]