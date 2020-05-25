#!/usr/bin/env bash

# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3

# LOG ANALYSIS
0 */4 * * *     $PY3    $HOME/$SENSORS/log_reader.py
32 3 20 * *     $PY3    $HOME/$SENSORS/log_remover.py -lvl debug
# SYS DATA COLLECTION
*/10 * * * *    $PY3    $HOME/$SENSORS/net/machine_uptime.py
# ENV DATA COLLECTION
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/garage_temps.py
*/5 * * * *     $PY3    $HOME/$SENSORS/presence/garage_door.py

