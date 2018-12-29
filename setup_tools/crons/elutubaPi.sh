#!/usr/bin/env bash

# sudo crontab -u root -e
# -----------------------------
0 0 * * * /sbin/shutdown -r now

# crontab -e
# -----------------------------
*/10 * * * * /usr/bin/python3 /home/pi/kavalkilu/sensors/temps/elutuba_temps.py
*/10 * * * * /usr/bin/python3 /home/pi/kavalkilu/sensors/temps/darksky_local_weather.py
*/10 * * * * /usr/bin/python3 /home/pi/kavalkilu/sensors/temps/darksky_tallinn_weather.py
*/10 * * * * /usr/bin/python3 /home/pi/kavalkilu/sensors/temps/darksky_rakvere_weather.py
