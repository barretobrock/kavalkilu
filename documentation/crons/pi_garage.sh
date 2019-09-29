#!/usr/bin/env bash

# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3

# NIGHTLY REBOOT @23.57
57 23 * * * root shutdown -r now
# LOG ANALYSIS
13 5 * * *      $PY3    $HOME/$SENSORS/log_reader.py
# SYS DATA COLLECTION
*/10 * * * *    $PY3    $HOME/$SENSORS/net/machine_uptime.py
# ENV DATA COLLECTION
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/garage_temps.py

