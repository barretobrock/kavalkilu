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
# LOG SCANNING STUFF
0 6 * * *           $PY3    $HOME/$SENSORS/log_reader.py
# PIHOLE STUFF
5 6 * * *           sh      $HOME/$SENSORS/pihole/pihole_backup.sh
# MYSQL STUFF
25 6 * * *          $PY3    $HOME/$SENSORS/pihole/pihole_to_mysql.py
35 6 * * *          $PY3    $HOME/$SENSORS/pihole/pihole_mysql_short_term_etl.py
0 2 * * *           $PY3    $HOME/$SENSORS/speedtest/speedtest_to_mysql.py
# AUTOMATION STUFF
0 */6 * * *        $PY3    $HOME/$SENSORS/speedtest/speedtest_logger.py
*/10 07-20 * * 1-5  $PY3    $HOME/$SENSORS/commute/commute_calc.py
*/10 * * * *        $PY3    $HOME/$SENSORS/temps/ecobee_temps.py
