#!/usr/bin/env bash

# sudo crontab -u root -e
# -----------------------------
0 0 * * * /sbin/shutdown -r now

# crontab -e
# -----------------------------
# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3

# LOG ANALYSIS
26 5 * * *       $PY3    $HOME/$SENSORS/log_reader.py
# SYS DATA COLLECTION
*/10 * * * *    $PY3    $HOME/$SENSORS/net/machine_uptime.py
# ENV DATA COLLECTION
*/10 * * * * $PY3 $HOME/$SENSORS/temps/porch_temps.py
