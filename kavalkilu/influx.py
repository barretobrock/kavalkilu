from datetime import datetime
from dateutil import tz
import pandas as pd
from typing import Union, List
from influxdb import InfluxDBClient
from .net import Hosts


class InfluxDBNames:
    HOMEAUTO = 'homeauto'


class InfluxTblNames:
    WEATHER = 'weather'
    TEMPS = 'temps'
    NETSPEED = 'net-speed'
    LOGS = 'logs'
    MACHINES = 'machine-activity'


class InfluxDBLocal(InfluxDBClient):
    def __init__(self, db: str, timezone: str = 'US/Central'):
        h = Hosts()
        super().__init__(h.get_ip_from_host('homeserv'), 8086, database=db)
        self.local_tz = tz.gettz(timezone)
        self.utc = tz.gettz('UTC')

    def _local_time_to_utc(self, obj: Union[datetime, str]) -> str:
        """Run if we're converting timestamps to UTC"""
        if isinstance(obj, str):
            obj = datetime.strptime(obj, '%Y-%m-%d %H:%M:%S')
        return obj.replace(tzinfo=self.local_tz).astimezone(self.utc).strftime('%F %T')

    def _utc_to_local_time(self, obj: Union[datetime, str]) -> str:
        """Run if we're converting timestamps to UTC"""
        if isinstance(obj, str):
            obj = datetime.strptime(obj, '%Y-%m-%dT%H:%M:%SZ')
        return obj.replace(tzinfo=self.utc).astimezone(self.local_tz).strftime('%F %T')

    def _build_json(self, tbl: str, row: pd.Series, tags: List[str],
                    value_cols: List[str], time_col: str = None):
        """Builds a single JSON object for a single item in a dataframe row
        NOTE: If time_col is None, the current time will be used.
        """
        json_dict = {
            'measurement': tbl,
            'tags': {x: row[x] for x in tags},
            'fields': {x: row[x] for x in value_cols}
        }
        if time_col is not None:
            json_dict['time'] = self._local_time_to_utc(row[time_col])

        return json_dict

    def write_single_data(self, tbl: str, tag_dict: dict, field_dict: dict, timestamp: datetime = None):
        """Writes a single group of data to the designated table"""
        json_dict = {
            'measurement': tbl,
            'tags': tag_dict,
            'fields': field_dict
        }
        if timestamp is not None:
            json_dict['time'] = self._local_time_to_utc(timestamp)
        self.write_points(json_dict)

    def write_df_to_table(self, tbl: str, df: pd.DataFrame, tags: Union[List[str], str],
                          value_cols: Union[List[str], str], time_col: str = None):
        """Writes a dataframe to the database"""
        if isinstance(value_cols, str):
            value_cols = [value_cols]
        if isinstance(tags, str):
            tags = [tags]

        batch = []
        for idx, row in df.iterrows():
            batch.append(self._build_json(tbl, row, tags, value_cols, time_col))

        self.write_points(batch)

    def read_query(self, query: str, time_col: str = None) -> pd.DataFrame:
        """Reads a query to pandas dataframe"""
        result = self.query(query)
        data = result.raw['series'][0]
        df = pd.DataFrame(data=data['values'], columns=data['columns'])
        # Convert time column to local
        if time_col is not None:
            df[time_col] = df[time_col].apply(lambda x: self._utc_to_local_time(x))

        return df

