#!/usr/bin/env bash

# sudo crontab -u root -e
# -----------------------------
0 0 * * * /sbin/shutdown -r now

# crontab -e
# -----------------------------
*/10 * * * * /usr/bin/python3 /home/pi/kavalkilu/sensors/temps/porch_temps.py
