import os
from typing import Optional
import pandas as pd
from pandas.core.dtypes.common import is_datetime_or_timedelta_dtype
import sqlite3


class SQLLiteLocal:
    """Common methods for interacting with SQLite data structures"""
    DEFAULT_DB_PATH = os.path.join(os.path.expanduser('~'), *['data', 'homeauto.sqlite'])

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.con = sqlite3.connect(db_path)

    def write_sql(self, query: str):
        """Write to table with query"""
        self.con.execute(query)
        self.con.commit()

    @staticmethod
    def _convert_rows_to_val_list(df: pd.DataFrame) -> str:
        """Converts rows in a dataframe to a nested tuple of values for insertion into a table"""
        val_list = []
        for idx, row in df.iterrows():
            val_row = ', '.join(f'"{val}"' for val in row.tolist())
            val_list.append(f'({val_row})')
        return f', '.join(val_list)

    def write_df_to_sql(self, tbl_name: str, df: pd.DataFrame, debug: bool = False) -> Optional[str]:
        """
        Generates an INSERT statement from a pandas DataFrame
        Args:
            tbl_name: str, name of the table to write to
            df: pandas.DataFrame
            debug: bool, if True, will only return the formatted query
        """
        # Develop a way to mass-insert a dataframe to a table, matching its format
        cols_joined = ', '.join(f'`{col}`' for col in df.columns)
        vals_str = self._convert_rows_to_val_list(df)
        query = f"""
            INSERT INTO {tbl_name} ({cols_joined})
            VALUES {vals_str}
        """
        if debug:
            return query
        else:
            self.write_sql(query)

    def read_sql(self, query: str) -> pd.DataFrame:
        """Query the database"""
        df = pd.read_sql_query(query, self.con)
        df = self._convert_times_to_local(df)
        return df

    @staticmethod
    def _convert_times_to_local(df: pd.DataFrame) -> pd.DataFrame:
        """SQLite by default stores timestamps in UTC. This should convert outputs to US/Central tz"""
        for col in df.columns.tolist():
            if is_datetime_or_timedelta_dtype(df[col]):
                # Convert from UTC to local tz
                df[col] = df[col].dt.tz_localize('utc').dt.tz_convert('US/Central')
        return df

    def __del__(self):
        """When last reference of this is finished, ensure the connection is closed"""
        self.con.close()
