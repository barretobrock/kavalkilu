#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu.tools import Paths, Log
from kavalkilu.tools.message import PBullet
import gspread
from collections import OrderedDict
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


def grab_timestamp(daily_df, activity, location, avg_time):
    """
    Searches through dataframe for certain activity at certain location.
    If no timestamp found for given combination, the average time string is processed
    Args:
        daily_df: pandas.DataFrame of day's activities at given locations
        activity: str, 'left' or 'arrived'
        location: str, location of activity
        avg_time: pandas.Timestamp, HH:MM of when activity at location takes place on average
    Returns:
        dictionary including timestamp and boolean whether the average time
            was used instead of the actual time.
    """
    adjusted = False

    # Filter dataframe basec on activity and location
    filtered_df = daily_df[(daily_df['activity'] == activity) & (daily_df['Location'] == location)]

    dd = daily_df.reset_index()

    if not filtered_df.empty:
        # If multiple results in filtered dataframe, apply logic to choose correctly:
        #   activity = 'left': pick first entry
        #   activity = 'arrived': pick last entry
        if filtered_df.shape[0] > 1:
            if activity == 'left':
                if 'WORK' in location:
                    # Leaving work = pick last entry
                    xrow = dd.loc[(dd['Location'] == location) & (dd['activity'] == activity)].index.tolist()[-1]
                elif 'HOME' in location:
                    # Leaving home = pick first entry
                    xrow = dd.loc[(dd['Location'] == location) & (dd['activity'] == activity)].index.tolist()[0]
            elif activity == 'arrived':
                if 'WORK' in location:
                    # Arriving to work = pick first entry
                    xrow = dd.loc[(dd['Location'] == location) & (dd['activity'] == activity)].index.tolist()[0]
                elif 'HOME' in location:
                    # Arriving home = pick first home entry after work
                    last_work_x = dd.loc[(dd['Location'] == 'BAO_WORK') & (dd['activity'] == 'left')].index.tolist()[-1]
                    last_work_ts = dd['timestamp'][last_work_x]
                    xrow = dd.loc[(dd['Location'] == location) & (dd['activity'] == activity) &
                                  (dd['timestamp'] > last_work_ts)].index.tolist()[0]
            tmstmp = dd.iloc[xrow]['timestamp']
        else:
            tmstmp = filtered_df.iloc[0]['timestamp']
    elif daily_df.empty:
        # Supplied dataframe is empty, so nothing can be done here
        return None
    else:
        tmstmp = pd.to_datetime(daily_df.iloc[0]['date']).replace(hour=avg_time.hour, minute=avg_time.minute)
        adjusted = True
    return {'tstamp': tmstmp, 'adjusted': adjusted}


def compile_day_timestamps(df):
    #today = df['date'].iloc[0]
    home_leave_norm = pd.to_datetime('07:35', format="%H:%M")
    work_arrive_norm = pd.to_datetime('08:25', format="%H:%M")
    work_leave_norm = pd.to_datetime('16:45', format="%H:%M")
    home_arrive_norm = pd.to_datetime('17:30', format="%H:%M")

    work_commute_norm = work_arrive_norm - home_leave_norm
    home_commute_norm = home_arrive_norm - work_leave_norm

    # Get timestamps
    ts_left_home = grab_timestamp(df, 'left', 'HOME', home_leave_norm)
    ts_arrived_work = grab_timestamp(df, 'arrived', 'BAO_WORK', work_arrive_norm)
    ts_left_work = grab_timestamp(df, 'left', 'BAO_WORK', work_leave_norm)
    ts_arrived_home = grab_timestamp(df, 'arrived', 'HOME', home_arrive_norm)

    # if ending timestamp is adjusted, readjust beginning and vice versa
    # Work commute
    if ts_left_home['adjusted'] and not ts_arrived_work['adjusted']:
        ts_left_home['tstamp'] = ts_arrived_work['tstamp'] - work_commute_norm
    elif not ts_left_home['adjusted'] and ts_arrived_work['adjusted']:
        ts_arrived_work['tstamp'] = ts_left_home['tstamp'] + work_commute_norm
    # Home commute
    if ts_left_work['adjusted'] and not ts_arrived_home['adjusted']:
        ts_left_work['tstamp'] = ts_arrived_home['tstamp'] - home_commute_norm
    elif not ts_left_work['adjusted'] and ts_arrived_home['adjusted']:
        ts_arrived_home['tstamp'] = ts_left_work['tstamp'] + home_commute_norm

    # Calculate minutes for commute, hours for time worked
    d = {
        'work_commute': pd.Timedelta(ts_arrived_work['tstamp'] - ts_left_home['tstamp']).seconds / 60,
        'adjusted_work_commute': any([ts_left_home['adjusted'], ts_arrived_work['adjusted']]),
        'hours_at_work': pd.Timedelta(ts_left_work['tstamp'] - ts_arrived_work['tstamp']).seconds / 60 / 60,
        'home_commute': pd.Timedelta(ts_arrived_home['tstamp'] - ts_left_work['tstamp']).seconds / 60,
        'adjusted_home_commute': any([ts_left_work['adjusted'], ts_arrived_home['adjusted']]),
    }
    return d


def get_metrics(df, todaydf, col_name, incl_adjusted):
    """
    Retireves min, mean and max of given column name in a pandas.DataFrame object
    Args:
        df: pandas.DataFrame object
        todaydf: pandas.DataFrame with similar structure as df, but filtered by today
        col_name: str, name of column to get desired metrics from
        incl_adjusted: boolean, include adjusted measurements in calculations
    """
    filtered_df = df[(df[col_name] > 0)]
    if not incl_adjusted:
        adj_col_name = 'adjusted_' + col_name
        if adj_col_name in filtered_df.columns:
            filtered_df = filtered_df[(-filtered_df[adj_col_name])]

    filtered_metric = filtered_df[col_name]

    metric_dict = {
        'current': todaydf[col_name].iloc[0],
        'metricmean': filtered_metric.mean(),
        'metricmin': filtered_metric.min(),
        'metricmax': filtered_metric.max(),
    }
    metric_dict['difference'] = metric_dict['current'] - metric_dict['metricmean']
    return metric_dict


def message_generator(activity_type, **kwargs):
    """
    Generates a message for commute statistic notifications
    Args:
        activity_type: str, ^((work|home)_commute|hours_at_work)$
    kwargs:
        ** dictionary from get_metrics()
    """
    if 'work_commute' == activity_type:
        msg_dict = {
            'wow': 'Woah!',
            'activity': 'got to work',
            'support': 'Good Job',
            'metric': 'Commute Time:',
            'unit': 'mins'
        }
    elif 'home_commute' == activity_type:
        msg_dict = {
            'wow': 'Cool!',
            'activity': 'got home',
            'support': 'Great',
            'metric': 'Commute Time:',
            'unit': 'mins'
        }
    elif 'hours_at_work' == activity_type:
        msg_dict = {
            'wow': 'Woah!',
            'activity': 'left work',
            'support': 'Super',
            'metric': 'Hours at Work:',
            'unit': 'hrs'
        }
    else:
        msg_dict = {
            'wow': 'Huh!',
            'activity': 'not sure what you did',
            'support': 'Still ok though',
            'metric': '?:',
            'unit': '?s'
        }
    msg_dict['minmetric'] = 'Min:'
    msg_dict['avgmetric'] = '*Average:'
    msg_dict['maxmetric'] = 'Max:'
    msg_dict['diff'] = '*Difference:'
    for k, v in kwargs.items():
        msg_dict[k] = v


    msg = """
    {wow} You just {activity}! {support}! Here are your stats:
    {metric:<14} {current:>6.2f} {unit}
    {avgmetric:<14} {metricmean:>6.2f} {unit}
    -----------------------------------
    {diff:<14} {difference:>+6.2f} {unit}
    -----------------------------------
    More Info:
    {minmetric:<14} {metricmin:>6.2f} {unit}
    {maxmetric:<14} {metricmax:>6.2f} {unit}
    """.format(**msg_dict)
    return msg


ymdfmt = '%Y-%m-%d %H:%M:%S'
p = Paths()

logg = Log('commute.calculator', 'commute', log_lvl="DEBUG")
logg.debug('Log initiated')

client_secret_path = p.google_client_secret
pb = PBullet(p.key_dict['pushbullet_api'])

csv_save_path = os.path.join(p.data_dir, 'commute_calculations.csv')

# Use creds to create a client to interact with Google Sheets API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret_path, scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
ws = client.open("Movement At Location")
sheet = ws.sheet1
processed_sheet = ws.worksheet('Processed')

# Check when the file was last updated
# Force ISO date format -- sometimes Google sheets cell will leave out leading '0's
last_update = pd.datetime.strptime(processed_sheet.cell(1, 2).value, ymdfmt).strftime(ymdfmt)

commute_df = pd.DataFrame(sheet.get_all_records())

# Begin processing columns
# First, Date columns
commute_df['timestamp'] = pd.to_datetime(commute_df['Raw_date'], format='%B %d, %Y at %I:%M%p')
last_entry = max(commute_df['timestamp']).strftime(ymdfmt)

if last_update < last_entry:
    logg.debug('New log found.')
    # New entry found, rerun calculations
    now = pd.datetime.now()
    # Refactor arrival/departure column
    commute_df['activity'] = ''
    commute_df.loc[commute_df.Activity == 'Left location', ['activity']] = 'left'
    commute_df.loc[commute_df.Activity == 'Arrived at location', ['activity']] = 'arrived'
    # Take out unused columns
    commute_df = commute_df[['activity', 'Location', 'timestamp']]
    # Determine work day [1 = Monday, 7 = Sunday]
    commute_df['date'] = commute_df.timestamp.apply(lambda x: x.date())

    min_date = min(commute_df['date'])
    max_date = max(commute_df['date'])
    date_range = pd.date_range(start=min_date, end=max_date)

    daily_commute_df = pd.DataFrame(OrderedDict((
        {
            'date': date_range.date,
            'dow': date_range.strftime('%u'),
            'adjusted_work_commute': False,
            'work_commute': 0,
            'hours_at_work': 0,
            'adjusted_home_commute': False,
            'home_commute': 0
        }))
    )

    for i in range(daily_commute_df.shape[0]):
        if int(daily_commute_df.loc[i, 'dow']) < 6:
            # work day
            df = commute_df[commute_df['date'] == daily_commute_df.loc[i, 'date']]
            if not df.empty:
                ts_dict = compile_day_timestamps(df)

                # Calculate minutes for work commute
                daily_commute_df.loc[i, 'work_commute'] = ts_dict['work_commute']
                daily_commute_df.loc[i, 'adjusted_work_commute'] = ts_dict['adjusted_work_commute']
                daily_commute_df.loc[i, 'hours_at_work'] = ts_dict['hours_at_work']
                daily_commute_df.loc[i, 'home_commute'] = ts_dict['home_commute']
                daily_commute_df.loc[i, 'adjusted_home_commute'] = ts_dict['adjusted_home_commute']

    # Save csv file
    logg.debug('Writing to csv.')
    daily_commute_df.to_csv(csv_save_path)

    # Loop through daily_commute_df and add to processed sheet on Google Sheets
    # Column title
    # processed_sheet.insert_row(daily_commute_df.columns.tolist(), index=1)
    # for i in range(daily_commute_df.shape[0]):
    #     row = daily_commute_df.iloc[i]
    #     row['date'] = row['date'].strftime('%Y-%m-%d')
    #     processed_sheet.insert_row(row.tolist(), index=i + 2)

    # Notify of my recent commute time
    latest_entry = commute_df[commute_df['timestamp'] == max(commute_df['timestamp'])].iloc[0]
    today_df = daily_commute_df[daily_commute_df['date'] == now.date()]
    msg = ''

    if latest_entry['activity'] == 'arrived' and latest_entry['Location'] == 'BAO_WORK':
        # Just arrived at work, analyze commute times
        # Generate message
        msg = message_generator('work_commute', **get_metrics(daily_commute_df, today_df, 'work_commute', False))
    elif latest_entry['activity'] == 'left' and latest_entry['Location'] == 'BAO_WORK':
        # Just arrived at work, analyze commute times
        # Generate message
        msg = message_generator('hours_at_work', **get_metrics(daily_commute_df, today_df, 'hours_at_work', False))
    elif latest_entry['activity'] == 'arrived' and latest_entry['Location'] == 'HOME':
        # Just arrived at work, analyze commute times
        # Generate message
        msg = message_generator('home_commute', **get_metrics(daily_commute_df, today_df, 'home_commute', False))

    if msg != '':
        logg.debug('Sending notification')
        pb.send_message('Commute Notification', msg)

    # Update cell with timestamp
    processed_sheet.update_cell(1, 2, pd.datetime.now().strftime(ymdfmt))

logg.close()
