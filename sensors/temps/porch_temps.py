"""Read temperatures from several locations outside using Dallas sensors"""

from time import sleep
from kavalkilu.tools.sensors import DallasTempSensor as daltemp
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal
from datetime import datetime
import os


# Serial numbers of the Dallas temp sensors
sensors = [
    {
        'sn': '28-0316b5f72bff',
        'loc': 'porch_upper_shade',
        'loc_id': 4
    }, {
        'sn': '28-0516a4a84eff',
        'loc': 'porch_upper_sun',
        'loc_id': 5
    }, {
        'sn': '28-0416c17b86ff',
        'loc': 'porch_lower_shade',
        'loc_id': 6
    }
]

oh = OpenHab()
# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = datetime.now().strftime('%H%M')
log = Log('porch_temp_{}'.format(log_suffix), 'temp', log_lvl='INFO')
log.debug('Logging initiated')

# Log motion into homeautodb
# Connect
ha_db = MySQLLocal('homeautodb')
conn = ha_db.engine.connect()

insert_query = """
    INSERT INTO temps (`loc_id`, `record_date`, `record_value`)
    VALUES ({loc_id}, "{ts}", {val})
"""

# Take measurement and record
temp_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for sensor in sensors:
    # Instantiate the temp sensors
    t = daltemp(sensor['sn'])
    sensor['val'] = t.measure()['temp']
    sensor['ts'] = temp_time
    # Update values in OpenHab
    sensor_name = 'Temp_{}'.format(sensor['loc'].replace('_', ' ').title().replace(' ', '_'))
    req = oh.update_value(sensor_name, '{}'.format(sensor['val']))
    sleep(1)
    formatted_query = insert_query.format(**sensor)
    insert_log = conn.execute(formatted_query)
    sleep(1)


conn.close()

log.debug('Temp logging successfully completed.')

log.close()
