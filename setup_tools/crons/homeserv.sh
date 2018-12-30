#!/usr/bin/env bash


# sudo crontab -u root -e
# -----------------------------
# Nightly backup of pihole queries
#0 15 * * * sqlite3 /etc/pihole/pihole-FTL.db ".backup /home/bobrock/data/pihole-FTL.db.backup"

# crontab -e
# -----------------------------
# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3
# PIHOLE STUFF
6,18 5 * * *        sh      $HOME/$SENSORS/pihole/pihole_backup.sh
# MYSQL STUFF
1 5 * * *           $PY3    $HOME/$SENSORS/pihole/pihole_to_mysql.py
2 * * * *           $PY3    $HOME/$SENSORS/speedtest/speedtest_to_mysql.py
# AUTOMATION STUFF
*/30 * * * *        $PY3    $HOME/$SENSORS/speedtest/speedtest_logger.py
*/10 07-20 * * 1-5  $PY3    $HOME/$SENSORS/commute/commute_calc.py
*/10 * * * *        $PY3    $HOME/$SENSORS/temps/ecobee_temps.py
