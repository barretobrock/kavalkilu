#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import json
import csv
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict
from .path import Paths
from .net import Keys


class MySQLLocal:
    """Stuff for connecting to local (LAN) MySQLdbs
    without having to remember the proper methods"""
    Base = declarative_base()

    def __init__(self, database_name, connection_dict=None):
        """
        Args:
            connection_dict: dict, contains connection credentials
                expects (un, pw, database, [port], [host])
        """
        p = Paths()
        k = Keys()

        if connection_dict is None:
            # Ignore connection dict, connecting to local/usual db
            # Read in username and password dict from path
            connection_dict = k.get_key('mysqldb')
            connection_dict['database'] = database_name
        # Determine if host and port is in dictionary, if not, use defaults
        if 'port' not in connection_dict.keys():
            connection_dict['port'] = 3306
        if 'host' not in connection_dict.keys():
            connection_dict['host'] = p.server_ip

        connection_url = 'mysql+mysqldb://{un}:{pw}@{host}:{port}/{database}'
        connection_url = connection_url.format(**connection_dict)
        self.engine = create_engine(connection_url)
        self.connection = self.engine.connect()

    def write_sql(self, query):
        """Writes a sql query to the database"""

        cursor = self.connection.begin()

        try:
            self.connection.execute(query)
            cursor.commit()
        except:
            cursor.rollback()
            raise

    def write_df_to_sql(self, tbl_name, df, debug=False):
        """
        Generates an INSERT statement from a pandas DataFrame
        Args:
            tbl_name: str, name of the table to write to
            df: pandas.DataFrame
            debug: bool, if True, will only return the formatted query
        """
        # Develop a way to mass-insert a dataframe to a table, matching its format
        query_base = """
            INSERT INTO {tbl} {cols}
            VALUES {vals}
        """
        query_dict = {
            'tbl': tbl_name,
            'cols': '({})'.format(', '.join('`{}`'.format(col) for col in df.columns)),
            'vals': ', '.join(
                ['({})'.format(', '.join('"{}"'.format(val) for val in row.tolist())) for idx, row in df.iterrows()])
        }
        formatted_query = query_base.format(**query_dict)
        if debug:
            return formatted_query
        else:
            query_log = self.write_sql(formatted_query)

    def write_dataframe(self, table_name, df):
        """
        Writes a pandas dataframe to database
        Args:
            table_name: str, name of the table in the database
            df: pandas.DataFrame
        """
        list_to_write = df.to_dict(orient='records')

        metadata = sqlalchemy.MetaData(bind=self.engine)
        table = sqlalchemy.Table(table_name, metadata, autoload=True)
        # Open the session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        self.connection.execute(table.insert(), list_to_write)

        session.commit()
        session.close()

    def __del__(self):
        """When last reference of this is finished, ensure the connection is closed"""
        self.connection.close()


class PiHoleDB:
    """Some static variables for pihole-level data"""
    # How query was handled
    #   Taken from https://docs.pi-hole.net/ftldns/database/#supported-status-types
    status_types = [
        {
            'status_id': 0,
            'desc': 'Unknown status (not answered by forward destination)',
            'status': 'unknown'
        }, {
            'status_id': 1,
            'desc': 'Blocked by gravity.list',
            'status': 'blocked'
        }, {
            'status_id': 2,
            'desc': 'Permitted + forwarded',
            'status': 'permitted'
        }, {
            'status_id': 3,
            'desc': 'Permitted + replied to from cache',
            'status': 'permitted'
        }, {
            'status_id': 4,
            'desc': 'Blocked by wildcard',
            'status': 'blocked'
        }, {
            'status_id': 5,
            'desc': 'Blocked by black.list',
            'status': 'blocked'
        }
    ]

    # Type of query made
    #   Taken from https://docs.pi-hole.net/ftldns/database/#supported-query-types
    query_types = [
        {
            'type_id': 1,
            'type': 'A'
        }, {
            'type_id': 2,
            'type': 'AAAA'
        }, {
            'type_id': 3,
            'type': 'ANY'
        }, {
            'type_id': 4,
            'type': 'SRV'
        }, {
            'type_id': 5,
            'type': 'SOA'
        }, {
            'type_id': 6,
            'type': 'PTR'
        }, {
            'type_id': 7,
            'type': 'TXT'
        }
    ]


class HomeAutoDB:
    def __init__(self, engine):
        self.engine = engine

    def temps_tbl(self):
        return Table('temps', sqlalchemy.schema.MetaData(bind=self.engine),
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('loc_id', Integer, primary_key=False),
                     Column('record_date', DateTime),
                     Column('record_value', Numeric()),
                     autoload=True,
                     extend_existing=True)


class GSheetReader:
    """A class to help with reading in Google Sheets"""
    def __init__(self, sheet_key):
        pyg = __import__('pygsheets')
        try:
            gsheets_creds = Keys().get_key('gsheet-reader')
        except:
            with open(os.path.join(os.path.expanduser('~'), *['keys', 'GSHEET_READER'])) as f:
                gsheets_creds = json.loads(f.read())
        os.environ['GDRIVE_API_CREDENTIALS'] = json.dumps(gsheets_creds)
        self.gc = pyg.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')
        self.sheets = self.gc.open_by_key(sheet_key).worksheets()

    def get_sheet(self, sheet_name):
        """Retrieves a sheet as a pandas dataframe"""
        for sheet in self.sheets:
            if sheet.title == sheet_name:
                return sheet.get_as_df()
        raise ValueError(f'The sheet name "{sheet_name}" was not found '
                         f'in the list of available sheets: ({",".join([x.title for x in self.sheets])})')

    def write_df_to_sheet(self, sheet_key, sheet_name, df):
        """Write df to sheet"""
        wb = self.gc.open_by_key(sheet_key)
        sheet = wb.worksheet_by_title(sheet_name)
        sheet.clear()
        sheet.set_dataframe(df, (1, 1))


class CSVHelper:
    """
    Handles CSV <-> OrderedDictionary reading/writing.
    Args for __init__:
        delimiter: character that delimits the CSV file. default: ';'
        linetermination: character that signals a line termination. default: '\n'
    """
    def __init__(self, delimiter=';', lineterminator='\n'):
        self.delimiter = delimiter
        self.lineterminator = lineterminator

    def csv_to_ordered_dict(self, path_to_csv, encoding='UTF-8'):
        """
        Imports CSV file to list of OrderedDicts
        Args:
            path_to_csv: str, path to csv file
            encoding: type of encoding to read in the file.
                default: 'UTF-8'
        """
        list_out = []
        with open(path_to_csv, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=self.delimiter, lineterminator=self.lineterminator)
            keys = next(reader)
            for row in reader:
                list_out.append(OrderedDict(zip(keys, row)))
        return list_out

    def csv_compacter(self, compacted_data_path, path_with_glob, sort_column='', remove_files=True):
        """
        Incorporates many like CSV files into one, with sorting for date column, if needed
        Args:
            compacted_data_path: path to file where compacted csv file will be saved.
                Doesn't have to exist
            path_with_glob: Full path where csv file group is taken. '*' is wildcard.
            sort_column: str, sorts combined data frame by given column name.
                Default = ''
            remove_files: bool, default = True
        """
        if os.path.exists(compacted_data_path):
            master_df = self.csv_to_ordered_dict(compacted_data_path)
        else:
            master_df = []

        list_of_files = glob.glob(path_with_glob)
        new_df_list = []
        if len(list_of_files) > 0:
            # Iterate through each file, combine
            for csvfile in list_of_files:
                df = self.csv_to_ordered_dict(csvfile)
                new_df_list += df
            master_df += new_df_list

            # Sort dataframe
            if sort_column != '':
                if sort_column.lower() in [x.lower() for x in master_df[0].keys()]:
                    # Determine the column to be sorted
                    for c in master_df[0].keys():
                        if c.lower() == sort_column.lower():
                            col = c
                            break
                    master_df = sorted(master_df, key=lambda k: k[col])
            # Save appended dataframe
            self.ordered_dict_to_csv(master_df, compacted_data_path)
            if remove_files:
                for csvfile in list_of_files:
                    os.remove(csvfile)

    def ordered_dict_to_csv(self, data_dict, path_to_csv, writetype='w'):
        """
        Exports given list of OrderedDicts to CSV
        Args:
            data_dict: OrderedDict or list of OrderedDicts to export
            path_to_csv: destination path to CSV file
            writetype: 'w' for writing or 'a' for appending
        """
        # saves list of list of ordered dicts to path
        # determine how deep to go: if list of lists, etc
        islistoflist = False
        if isinstance(data_dict[0], list):
            if isinstance(data_dict[0][0], OrderedDict):
                islistoflist = True

        with open(path_to_csv, writetype) as f:
            if islistoflist:
                keys = data_dict[0][0].keys()
            else:
                keys = data_dict[0].keys()
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore', delimiter=self.delimiter,
                                    lineterminator=self.lineterminator)
            # If appending, don't write a header string
            if writetype == 'w':
                writer.writeheader()
            # Write data to file based on depth
            if islistoflist:
                for row in data_dict:
                    writer.writerows(row)
            else:
                writer.writerows(data_dict)
