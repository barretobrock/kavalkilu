#!/usr/bin/env bash

# sudo crontab -u root -e
# -----------------------------
0 0 * * * /sbin/shutdown -r now

# crontab -e
# -----------------------------
# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3
# TEMPERATURE STUFF
*/10 * * * * $PY3 $HOME/$SENSORS/temps/porch_temps.py
