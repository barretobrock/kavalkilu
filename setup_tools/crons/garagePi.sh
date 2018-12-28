#!/usr/bin/env bash


# sudo crontab -u root -e
# -----------------------------
0 0 * * * /sbin/shutdown -r now

# crontab -e
# -----------------------------
*/5 * * * *     python3         /home/pi/kavalkilu/sensors/garage_motion.py
*/10 * * * *    python3         /home/pi/kavalkilu/sensors/temps/garage_temps.py
