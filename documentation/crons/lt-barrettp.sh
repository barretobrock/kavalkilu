#!/usr/bin/env bash

# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/home/bobrock/venvs/kavkil/bin/python3

# Vpulse Automation
0 5 * * * export DISPLAY=:0; $PY3 $HOME/$SENSORS/vpulse/vpulse_auto.py
