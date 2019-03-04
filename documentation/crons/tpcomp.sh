#!/usr/bin/env bash


# sudo crontab -u root -e
# -----------------------------

# crontab -e
# -----------------------------
# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3

# Vpulse Automation
40 03 * * * export DISPLAY=:0; python3 ~/kavalkilu/tests/vpulse_auto.py
