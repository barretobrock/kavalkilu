#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from .path import Paths


class MySQLLocal:
    """Stuff for connecting to local (LAN) MySQLdbs
    without having to remember the proper methods"""

    def __init__(self, database_name, connection_dict=None):
        """
        Args:
            connection_dict: dict, contains connection credentials
                expects (un, pw, database, [port], [host])
        """
        p = Paths()

        if connection_dict is None:
            # Ignore connection dict, connecting to local/usual db
            # Read in username and password dict from path
            connection_dict = p.key_dict['mysqldb']
            connection_dict['database'] = database_name
        # Determine if host and port is in dictionary, if not, use defaults
        if 'port' not in connection_dict.keys():
            connection_dict['port'] = 3306
        if 'host' not in connection_dict.keys():
            connection_dict['host'] = p.server_ip

        connection_url = 'mysql+mysqldb://{un}:{pw}@{host}:{port}/{database}'
        connection_url = connection_url.format(**connection_dict)
        self.engine = create_engine(connection_url)
