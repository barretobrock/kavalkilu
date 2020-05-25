#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sqlite3
import pandas as pd


def create_connection(fpath):
    """
    Creates a READ-only database connection to a SQLite database, located at the file path
    :param fpath: str, path to the database file
    :return: connection object
    """
    try:
        conn = sqlite3.connect('file:{}?mode=ro'.format(fpath), uri=True)
    except Exception as e:
        print(e)
        conn = None
    return conn


accts_path = os.path.join('/home/bobrock', 'Dropbox/Finance/GNUCash/EelarveSQLLite.gnucash')
conn = create_connection(accts_path)

accounts = pd.read_sql_query('SELECT * FROM accounts;', conn)

transactions = pd.read_sql_query('SELECT * FROM transactions LIMIT 10;', conn)

splits = pd.read_sql_query('SELECT * FROM splits LIMIT 10;', conn)

daily_balance_query = """
SELECT
    a.name AS account
    , STRFTIME('%Y-%m-%d', t.post_date) AS day
    , SUM(sp.value_num) * 0.01 AS value
FROM
    splits AS sp
INNER JOIN
    transactions AS t ON sp.tx_guid = t.guid
INNER JOIN
    accounts AS a ON sp.account_guid = a.guid
WHERE
    a.parent_guid = 'e4f00eecd1e345d467470b2ca6979766'
GROUP BY
    a.name
    , STRFTIME('%Y-%m-%d', t.post_date)
"""


df3 = pd.read_sql_query(daily_balance_query, conn)
