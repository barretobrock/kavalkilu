#!/usr/bin/env bash


# sudo crontab -u root -e
# -----------------------------
# Nightly backup of pihole queries
0 15 * * * sqlite3 /etc/pihole/pihole-FTL.db ".backup /home/bobrock/data/pihole-FTL.db.backup"

# crontab -e
# -----------------------------
# MYSQL STUFF
0 * * * * /usr/bin/python3 /home/bobrock/scripts/pihole_to_mysqldb.py
2 * * * * /usr/bin/python3 /home/bobrock/scripts/speedtest_to_mysql.py
# AUTOMATION STUFF
*/30 * * * * /usr/bin/python3 /home/bobrock/blue2/comm/speedtest_logger.py
*/10 07-20 * * 1-5 /usr/bin/python3 /home/bobrock/blue2/agg/commute_calc.py
*/10 * * * * /usr/bin/python3 /home/bobrock/kavalkilu/sensors/temps/ecobee_temps.py
