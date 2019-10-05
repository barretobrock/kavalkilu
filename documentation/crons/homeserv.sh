#!/usr/bin/env bash

# VARIABLES
SENSORS=kavalkilu/sensors
PY3=/usr/bin/python3

# LOG ANALYSIS
0 6 * * *           $PY3    $HOME/$SENSORS/log_reader.py
# PIHOLE
5 6 * * *           bash    $HOME/$SENSORS/pihole/pihole_backup.sh
# MYSQL
25 6 * * *          $PY3    $HOME/$SENSORS/pihole/pihole_to_mysql.py
35 6 * * *          $PY3    $HOME/$SENSORS/pihole/pihole_mysql_short_term_etl.py
0 2 * * *           $PY3    $HOME/$SENSORS/speedtest/speedtest_to_mysql.py
# SYS DATA COLLECTION
*/10 * * * *        $PY3    $HOME/$SENSORS/net/machine_uptime.py
*/5 03-22 * * *     $PY3    $HOME/$SENSORS/net/mobile_connected.py
0 */6 * * *         $PY3    $HOME/$SENSORS/speedtest/speedtest_logger.py
# ENV DATA COLECTION
*/10 * * * *        $PY3    $HOME/$SENSORS/temps/ecobee_temps.py
# HOME AUTOMATION
*/10 03-22 * * *    $PY3    $HOME/$SENSORS/camera/amcrest_notify_zone.py
5 23 * * *          $PY3    $HOME/$SENSORS/camera/amcrest_nighttime.py
*/5 * * * *         $PY3    $HOME/$SENSORS/presence/garage_door.py
# SLACK
@reboot             $PY3    $HOME/$SENSORS/slackbot/kodubot_rtm_daemon.py start
15 */4 * * *        $PY3    $HOME/$SENSORS/slackbot/slack_logger.py

# Vpulse Automation
40 03 * * * export DISPLAY=:0; python3 $HOME/$SENSORS/vpulse/vpulse_auto.py

# HOSTS API
@reboot bash $HOME/kavalkilu/apis/hosts/start_service.sh
