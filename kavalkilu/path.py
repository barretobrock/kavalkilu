"""Builds common paths"""
import os
import argparse
from typing import List, Union


class ArgParser:
    """Argument parsing wrapper"""
    def __init__(self, desc: str):
        self.parser = argparse.ArgumentParser()

    def add_named_arg(self):
        """Adds a named argument to the parser"""
        self.parser.add_argument()


class Path:
    """Wrapper class that stores common paths and common methods for handling paths"""
    def __init__(self, user: str = ''):
        home = os.path.expanduser(f'~{user}')
        self.data_dir = os.path.join(home, 'data')
        self.keys_dir = os.path.join(home, 'keys')
        self.logs_dir = os.path.join(home, 'logs')
        self.extras_dir = os.path.join(home, 'extras')
        self.venvs_dir = os.path.join(home, 'venvs')
        self.download_dir = os.path.join(home, 'Downloads')

    @staticmethod
    def easy_joiner(parent: str, paths: Union[str, List[str]]) -> str:
        """Provides an easy way to join a path"""
        if isinstance(paths, str):
            paths = [paths]
        return os.path.join(parent, *paths)

    @staticmethod
    def get_extension(path: str) -> str:
        """Gets the file extension of a path"""
        return os.path.splitext(path)[1]

    @staticmethod
    def exists(path: str) -> bool:
        """Determines if the file exists"""
        return os.path.exists(path)
