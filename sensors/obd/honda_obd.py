#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import obd
from datetime import datetime as dt
import time
from collections import OrderedDict
from kavalkilu.tools import Paths, Log
from kavalkilu.tools.databases import CSVHelper


def is_engine_on(conn):
    """Determines if engine is running"""
    val = try_collect(conn, 'RPM')
    if val is None:
        return False
    else:
        return True


def try_collect(conn, cmd):
    """
    Attempts to collect data on the particular command.
    Args:
        conn: obd-class connection
        cmd: str, type of metric
    """
    try:
        response = conn.query(obd.commands[cmd])
        rval = response.value.magnitude
    except:
        rval = None
    return rval


measurement_interval = 1  # time to wait between measurements
sleep_interval = 10  # time to wait in seconds between "engine pings"

p = Paths()
logg = Log('honda_obd', 'obd_logger', log_lvl="DEBUG")
logg.debug('Logging initiated')

chelp = CSVHelper()
# Set path to write file to
save_path = os.path.join(p.data_dir, 'obd_results_{}.csv'.format(dt.now().strftime('%Y%m%d_%H%M%S')))

# Get commands
cmd_list = [x.name for x in obd.commands[1][4:]]

result_dicts = []
t = time.time()
end_time = t + 60 * 5   # Run for five minutes
end_time -= 5   # Take off five seconds for processing

try:
    connection = obd.OBD()
    is_connected = True
except:
    is_connected = False
    pass

while time.time() < end_time:
    if not is_connected:
        # Make sure bluetooth is connected. Otherwise try connecting to it
        # Attempt to make connection.
        try:
            connection = obd.OBD()
            is_connected = True
        except:
            is_connected = False
            pass

        if not is_connected:
            # Sleep if still no success
            time.sleep(sleep_interval)
    else:
        if is_engine_on(connection):
            logg.debug("Engine detected as 'ON'. Beginning recording")
            # If engine is on, being recording...
            while is_engine_on(connection) and time.time() < end_time:
                line_dict = OrderedDict(())
                line_dict['TIMESTAMP'] = dt.now().isoformat()
                for d in cmd_list:
                    rval = try_collect(connection, d)

                    # Append to dictionary
                    line_dict[d] = rval

                # Append line of data to main dictionary
                result_dicts.append(line_dict)
                # Wait a second before continuing
                time.sleep(measurement_interval)

            logg.debug('Loop ended. Writing file.')
            # Save file
            chelp.ordered_dict_to_csv(result_dicts, save_path)
        else:
            time.sleep(sleep_interval)

logg.close()
