from datetime import datetime
import pandas as pd
from typing import Union, List
from influxdb import InfluxDBClient
from .net import Hosts
from .date import DateTools
from .path import HOME_SERVER_HOSTNAME


class InfluxTable:
    """Class for combining influx table name with the database it's stored in"""
    def __init__(self, db: str, name: str):
        self.table = name
        self.database = db


class InfluxDBHomeAuto:
    """homeauto Influx database + tables"""
    database = 'homeauto'
    CPU = InfluxTable(database, 'cpu')
    CPUTEMP = InfluxTable(database, 'cputemp')
    DISK = InfluxTable(database, 'disk')
    LOGS = InfluxTable(database, 'logs')
    MACHINES = InfluxTable(database, 'machine-activity')
    MEM = InfluxTable(database, 'mem')
    NETSPEED = InfluxTable(database, 'net-speed')
    TEMPS = InfluxTable(database, 'temps')
    WEATHER = InfluxTable(database, 'weather')


class InfluxDBPiHole:
    """pihole Influx database + tables"""
    database = 'pihole'
    QUERIES = InfluxTable(database, 'queries')


class InfluxDBTracker:
    """tracker Influx database + tables"""
    database = 'tracker'
    APT_PRICES = InfluxTable(database, 'apt_prices')


class InfluxDBLocal(InfluxDBClient):
    def __init__(self, dbtable: InfluxTable, timezone: str = 'US/Central'):
        h = Hosts()
        self.database = dbtable.database
        self.table = dbtable.table
        super().__init__(h.get_ip_from_host(HOME_SERVER_HOSTNAME), 8086, database=self.database)
        self.dt = DateTools()
        self.local_tz = timezone
        self.utc = 'UTC'

    def _build_json(self, row: pd.Series, tags: List[str],
                    value_cols: List[str], time_col: str = None):
        """Builds a single JSON object for a single item in a dataframe row
        NOTE: If time_col is None, the current time will be used.
        """
        json_dict = {
            'measurement': self.table,
            'tags': {x: row[x] for x in tags},
            'fields': {x: row[x] for x in value_cols}
        }
        if time_col is not None:
            json_dict['time'] = self.dt.local_time_to_utc(row[time_col], local_tz=self.local_tz, as_str=True)

        return json_dict

    def write_single_data(self, tag_dict: dict, field_dict: dict, timestamp: datetime = None):
        """Writes a single group of data to the designated table"""
        json_dict = {
            'measurement': self.table,
            'tags': tag_dict,
            'fields': field_dict
        }
        if timestamp is not None:
            json_dict['time'] = self.dt.local_time_to_utc(timestamp, local_tz=self.local_tz, as_str=True)
        self.write_points([json_dict])

    def write_df_to_table(self, df: pd.DataFrame, tags: Union[List[str], str],
                          value_cols: Union[List[str], str], time_col: str = None):
        """Writes a dataframe to the database"""
        if isinstance(value_cols, str):
            value_cols = [value_cols]
        if isinstance(tags, str):
            tags = [tags]

        batch = []
        for idx, row in df.iterrows():
            batch.append(self._build_json(row, tags, value_cols, time_col))

        self.write_points(batch)

    def read_query(self, query: str, time_col: str = None) -> pd.DataFrame:
        """Reads a query to pandas dataframe"""
        result = self.query(query)
        series = result.raw['series']
        if len(series) == 0:
            return pd.DataFrame()
        result_df = pd.DataFrame()
        for s in series:
            columns = s.get('columns', [])
            values = s.get('values', [])
            df = pd.DataFrame(data=values, columns=columns)
            if s.get('tags') is not None:
                for k, v in s.get('tags', {}).items():
                    df[k] = v
            result_df = result_df.append(df)
        result_df = result_df.reset_index(drop=True)
        # Convert time column to local
        if time_col is not None:
            # Convert the time column to Central TZ
            result_df[time_col] = pd.to_datetime(result_df[time_col]).dt\
                .tz_convert('US/Central').dt.strftime('%F %T')

        return result_df
