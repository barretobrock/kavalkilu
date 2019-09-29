#!/usr/bin/env bash

# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3

# LOG ANALYSIS
39 5 * * *       $PY3    $HOME/$SENSORS/log_reader.py
# SYS DATA COLLECTION
*/10 * * * *    $PY3    $HOME/$SENSORS/net/machine_uptime.py
# ENV DATA COLLECTION
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/elutuba_temps.py
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/darksky_weather.py
