from datetime import datetime
from typing import (
    Dict,
    List,
    Union,
)

from influxdb import InfluxDBClient
import pandas as pd
from pukr import PukrLog

from kavalkilu.date import DateTools
from kavalkilu.net import (
    Hosts,
    NetTools,
)
from kavalkilu.path import HOME_SERVER_HOSTNAME


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
    def __init__(self, dbtable: InfluxTable, app_name: str = 'unnamed app',
                 timezone: str = 'US/Central'):
        h = Hosts()
        self.database = dbtable.database
        self.table = dbtable.table
        self.machine = NetTools.get_hostname()
        self.app_name = app_name
        super().__init__(h.get_ip_from_host(HOME_SERVER_HOSTNAME), 8086, database=self.database)
        self.dt = DateTools()
        self.local_tz = timezone
        self.utc = 'UTC'

    def _build_json(self, row: pd.Series, tags: List[str],
                    value_cols: List[str], time_col: str = None) -> Dict:
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

    def write_single_data(self, tag_dict: Dict, field_dict: Dict, timestamp: datetime = None):
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

    def read_query_to_dataframe(self, query: str, time_col: str = None) -> pd.DataFrame:
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

    def log_exception(self, err_obj: Exception):
        err_txt = str(err_obj)
        err_class = err_obj.__class__.__name__ if err_obj is not None else 'NA'
        log_dict = {
            'machine': self.machine,
            'name': self.app_name,
            'level': 'ERROR',
            'class': err_class,
            'text': err_txt
        }
        field_dict = {
            'entry': 1
        }
        self.write_single_data(tag_dict=log_dict, field_dict=field_dict)

    def influx_exception_decorator(self, logger: PukrLog):
        """
        Decorator for capturing exceptions and logging them to influx and the log object

        Example:
            >>>@inflx.influx_exception_decorator(logger=log)
            >>>def my_func():
            >>>     return 'whatever'
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Log exception
                    self.log_exception(e)
                    logger.exception(e)
                    # Re-raise exception
                    raise
            return wrapper
        return decorator

    def influx_exception_hook(self, exc_type, exc_value, exc_traceback):
        """
        Exception catcher for use with sys.excepthook

        Note:
            Use with the decorator is not recommended - this will result in duplication of the exception logged

        Example:
            >>> sys.excepthook = inflx.influx_exception_hook
        """
        self.log_exception(exc_value)
        raise exc_value


if __name__ == '__main__':
    import sys

    from pukr import get_logger

    inflx = InfluxDBLocal(dbtable=InfluxDBHomeAuto.LOGS, machine='test', app_name='test_app')
    log = get_logger('test_log')
    sys.excepthook = inflx.influx_exception_hook

    @inflx.influx_exception_decorator(logger=log)
    def thang():
        return 1/0

    thang()
