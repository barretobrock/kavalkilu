"""Collect local temperature data"""

from kavalkilu.tools.weather import DarkSkyWeather
import pandas as pd


local_latlong = '30.3428,-97.7582'
dsky = DarkSkyWeather(local_latlong)
dsky_data = dsky.get_data()


def format_tables(data, tz='US/Central'):
    """Takes in a grouping of data and returns as a pandas dataframe"""
    if isinstance(data, list):
        # Dealing with multiple rows of data
        df = pd.DataFrame(data)
    elif isinstance(data, dict):
        # Dealing with a single row of data
        df = pd.DataFrame(data, index=[0])

    # Convert any "time" column to locally-formatted datetime
    time_cols = [col for col in df.columns if 'time' in col.lower()]
    if len(time_cols) > 0:
        for time_col in time_cols:
            # Convert column to datetime
            dtt_col = pd.to_datetime(df[time_col], unit='s')
            # Convert datetime col to local timezone and remove tz
            dtt_col = dtt_col.dt.tz_localize('utc').dt.tz_convert(tz).dt.tz_localize(None)
            df[time_col] = dtt_col

    return df





data.keys()

current_df = pd.DataFrame(data['currently'], index=[0])