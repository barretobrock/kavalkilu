#!/usr/bin/env bash

# sudo crontab -u root -e
# -----------------------------
0 0 * * * /sbin/shutdown -r now

# crontab -e
# -----------------------------
# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3
# WEATHER DATA
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/elutuba_temps.py
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/darksky_local_weather.py
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/darksky_tallinn_weather.py
*/10 * * * *    $PY3    $HOME/$SENSORS/temps/darksky_rakvere_weather.py
