"""Read temperature and humidity from garage"""
from time import sleep
from kavalkilu.tools.sensors import DHTTempSensor as DHT
from kavalkilu.tools.openhab import OpenHab
from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal
from datetime import datetime
import os


# Set the pin
TEMP_PIN = 24
oh = OpenHab()
# Initiate Log, including a suffix to the log name to denote which instance of log is running
log_suffix = datetime.now().strftime('%H%M')
log = Log('garage_temp_{}'.format(log_suffix), os.path.abspath('/home/pi/logs'), 'temp', 'INFO')
log.debug('Logging initiated')
# Instantiate the temp sensor
tsensor = DHT(TEMP_PIN, decimals=3)

n_reads = 5
# Take five readings, pick the average
readings = []
for x in range(0, 5):
    readings.append(tsensor.measure())
    sleep(2)

temp_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
temp_avg = float(sum(d['temp'] for d in readings)) / len(readings)
hum_avg = float(sum(d['humidity'] for d in readings)) / len(readings)

# Update values in OpenHab
for name, val in zip(['Env_Garaaz_DHT', 'Temp_Garaaz', 'Hum_Garaaz'], [temp_time, temp_avg, hum_avg]):
    req = oh.update_value(name, '{}'.format(val))

# Log motion into homeautodb
# Connect
ha_db = MySQLLocal('homeautodb')
conn = ha_db.engine.connect()
# Find garage location
location_resp = conn.execute('SELECT id FROM locations WHERE location = "garage"')
for row in location_resp:
    loc_id = row['id']
    break

# Build a dictionary of the values we're moving around
val_dict = {
    'ts': temp_time,
    'temp': temp_avg,
    'hum': hum_avg,
    'temp_db': 'temps',
    'hum_db': 'humidity',
    'loc': loc_id
}
# Write timestamp and temps to garage location
insertion_query = """
    INSERT INTO {temp_db} (`loc_id`, `record_date`, `record_value`) VALUES ({loc}, "{ts}", {temp});
    INSERT INTO {hum_db} (`loc_id`, `record_date`, `record_value`) VALUES ({loc}, "{ts}", {hum});
    """.format(**val_dict)
temp_log = conn.execute(insertion_query)
conn.close()

log.debug('Temp logging successfully completed.')

log.close()
