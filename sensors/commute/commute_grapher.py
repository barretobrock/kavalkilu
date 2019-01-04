#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from kavalkilu import Paths, Log
import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.offline as pyoff
import plotly.graph_objs as go
import json


def dow_boxplot(df, data_col, dow_col, save_dir, incl_weekend=False, plot_online=False):
    """
    Uses plotly package to graph a box plot + mean line graph of data,
        grouped by day of week (DOW)
    Args:
        df: pandas.DataFrame containing the data
        data_col: str, column name containing the data to examine
        dow_col: column name containing the day of week
        save_dir: directory to save image/html file to
        incl_weekend: boolean, include weekend days in graph
    """

    title_portion = data_col.replace('_', ' ').title()
    file_name = '{}_graph'.format(data_col)
    png_file_path = os.path.join(save_dir, '{}.png'.format(file_name))

    marker_dict = {
        'size': 10,
        'color': 'rgba(255, 182, 193, .9)',
        'line': {
            'width': 2
        }
    }

    # Sort by DOW
    df['dow'] = df['dow'].astype(int)
    df = df.sort_values(by=dow_col)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if not incl_weekend:
        # Remove weekend days
        df = df[df[dow_col] < 6]
        days = days[:5]

    # Get mean for each DOW
    mean_by_dow = df.groupby(by=dow_col)[data_col].mean()
    # Begin populating data list
    data = []
    for d in df[dow_col].unique().tolist():
        data.append(go.Box(y=df[df[dow_col] == d][data_col], name=days[d - 1], showlegend=False))

    data.append(go.Scatter(x=days, y=mean_by_dow, mode='lines+markers', name='mean', marker=marker_dict))

    if 'hour' in data_col:
        yax_title = 'Time Worked (hrs)'
    else:
        yax_title = 'Commute Time (mins)'

    layout = go.Layout(
        title='{} Stats by Day'.format(title_portion),
        xaxis={
            'title': 'Day of Week',
        },
        yaxis={
            'title': yax_title,
            'rangemode': 'tozero'
        },
        width=800,
        height=640
    )
    fig = go.Figure(data=data, layout=layout)

    py.image.save_as(fig, filename=png_file_path)
    if plot_online:
        # Save plot online (to put on website)
        py.plot(fig, filename=file_name)


def mon_boxplot(df, data_col, mon_col, save_dir, plot_online=False):
    """
    Uses plotly package to graph a box plot + mean line graph of data,
        grouped by month
    Args:
        df: pandas.DataFrame containing the data
        data_col: str, column name containing the data to examine
        mon_col: column name containing the month
        save_dir: directory to save image/html file to
    """

    title_portion = data_col.replace('_', ' ').title()
    file_name = '{}_monthly_graph'.format(data_col)
    png_file_path = os.path.join(save_dir, '{}.png'.format(file_name))

    marker_dict = {
        'size': 10,
        'color': 'rgba(255, 182, 193, .9)',
        'line': {
            'width': 2
        }
    }

    # Sort by month
    df['month'] = df['month'].astype(int)
    df = df.sort_values(by=mon_col)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Get mean for each month
    mean_by_mon = df.groupby(by=mon_col)[data_col].mean()
    mean_df = pd.DataFrame(index=np.arange(1, 13), data={
        'mean': mean_by_mon
    })
    annual_mean = np.mean(mean_df['mean'])
    mean_df['mean'] = mean_df['mean'].fillna(annual_mean)
    mean_df['month_name'] = months
    # Begin populating data list
    data = []
    for d in mean_df.index.tolist():
        month_data = df[df[mon_col] == d][data_col]
        if month_data.shape[0] == 0:
            month_data = pd.Series([annual_mean] * 5)
        data.append(go.Box(y=month_data, name=months[d - 1], showlegend=False))

    data.append(go.Scatter(x=months, y=mean_df['mean'], mode='lines+markers', name='mean', marker=marker_dict))

    if 'hour' in data_col:
        yax_title = 'Time Worked (hrs)'
    else:
        yax_title = 'Commute Time (mins)'

    layout = go.Layout(
        title='{} Stats by Month'.format(title_portion),
        xaxis={
            'title': 'Month',
        },
        yaxis={
            'title': yax_title,
            'rangemode': 'tozero'
        },
        width=800,
        height=640
    )
    fig = go.Figure(data=data, layout=layout)

    py.image.save_as(fig, filename=png_file_path)
    if plot_online:
        # Save plot online (to put on website)
        py.plot(fig, filename=file_name)


p = Paths()

logg = Log('commute_grapher', 'commute', log_lvl="DEBUG")
logg.debug('Log initiated')

api = json.loads(p.key_dict['plotly_api'])

csv_path = os.path.join(p.data_dir, 'commute_calculations.csv')
# Import csv data
commute_df = pd.read_csv(csv_path, index_col=0, delimiter=',', lineterminator='\n')

# Insert month column
commute_df['month'] = commute_df['date'].apply(lambda x: pd.datetime.strptime(x, '%Y-%m-%d').month)

# Take out measurements larger than 90 minutes
commute_df = commute_df[(commute_df.work_commute < 90) & (commute_df.home_commute < 90)]
commute_df = commute_df[(commute_df.work_commute > 0) & (commute_df.home_commute > 0)]

# Read in pyplot credentials
py.sign_in(username=api['username'], api_key=api['api_key'])

dow_boxplot(commute_df, 'work_commute', 'dow', p.data_dir, incl_weekend=False, plot_online=False)
dow_boxplot(commute_df, 'hours_at_work', 'dow', p.data_dir, incl_weekend=False, plot_online=False)
dow_boxplot(commute_df, 'home_commute', 'dow', p.data_dir, incl_weekend=False, plot_online=False)
mon_boxplot(commute_df, 'home_commute', 'month', p.data_dir, plot_online=False)
mon_boxplot(commute_df, 'work_commute', 'month', p.data_dir, plot_online=False)
mon_boxplot(commute_df, 'hours_at_work', 'month', p.data_dir, plot_online=False)

logg.close()