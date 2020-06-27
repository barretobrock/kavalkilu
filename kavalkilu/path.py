"""Builds common paths"""
import os
from typing import List, Union


class Path:
    """Wrapper class that stores common paths and common methods for handling paths"""
    def __init__(self):
        home = os.path.expanduser('~')
        self.data_dir = os.path.join(home, 'data')
        self.keys_dir = os.path.join(home, 'keys')
        self.logs_dir = os.path.join(home, 'logs')
        self.venvs_dir = os.path.join(home, 'venvs')
        self.download_dir = os.path.join(home, 'Downloads')

    @staticmethod
    def easy_joiner(parent: str, paths: Union[str, List[str]]) -> str:
        """Provides an easy way to join a path"""
        return os.path.join(parent, paths)

    @staticmethod
    def get_extension(path: str) -> str:
        """Gets the file extension of a path"""
        return os.path.splitext(path)[1]

    @staticmethod
    def exists(path: str) -> bool:
        """Determines if the file exists"""
        return os.path.exists(path)