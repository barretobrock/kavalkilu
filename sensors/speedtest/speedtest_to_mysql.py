import os
import datetime
from datetime import datetime as dtt
import pandas as pd
import numpy as np
from kavalkilu.tools import Paths
from kavalkilu.tools.databases import MySQLLocal


p = Paths()
filepath = os.path.join(os.path.abspath(p.data_dir), 'speedtest_data.csv')

# Connect to db
conn = MySQLLocal('speedtestdb').engine.connect()
# Establish transaction
trans = conn.begin()

# Read in our speedtest data
speedtest_df = pd.read_csv(filepath)

# Get the period of data to input (previous hour's data)
ts_start = (dtt.now() - datetime.timedelta(hours=1)).replace(minute=0, second=0).strftime('%FT%T')
ts_end = dtt.now().replace(minute=0, second=0).strftime('%FT%T')

# Slice out the day's test results
sliced = speedtest_df[(ts_start <= speedtest_df.TIMESTAMP) & (speedtest_df.TIMESTAMP < ts_end)]

sliced.loc[:, 'TIMESTAMP'] = pd.to_datetime(sliced.TIMESTAMP).dt.strftime('%F %T')
sliced.loc[:, ['DOWNLOAD', 'UPLOAD']] = sliced[['DOWNLOAD', 'UPLOAD']].applymap(lambda x: round(float(x), 4))
sliced = sliced[['TIMESTAMP', 'DOWNLOAD', 'UPLOAD']]

for i in range(sliced.shape[0]):
    row = sliced.iloc[i, :]
    d = {
        'timestamp': row['TIMESTAMP'],
        'download': float(row['DOWNLOAD']),
        'upload': float(row['UPLOAD']),
    }
    query = """
        INSERT INTO speedtestdb.speedtest (`test_date`, `download`, `upload`)
        VALUES ('{timestamp}', {download}, {upload})
    """.format(**d)
    try:
        conn.execute(query)
        trans.commit()
    except:
        trans.rollback()

conn.close()

# Rewrite CSV file as being the last 10 entries
speedtest_df = speedtest_df[['TIMESTAMP', 'DOWNLOAD', 'UPLOAD']].tail(10)
speedtest_df.to_csv(filepath, index=False)






