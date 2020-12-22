"""Builds common paths"""
import os
from typing import List, Union

HOME_SERVER_HOSTNAME = 'tinyserv'


class Path:
    """Wrapper class that stores common paths and common methods for handling paths"""
    def __init__(self, user: str = ''):
        home = os.path.expanduser(f'~{user}')
        self.pth = os.path
        self.data_dir = os.path.join(home, 'data')
        self.keys_dir = os.path.join(home, 'keys')
        self.logs_dir = os.path.join(home, 'logs')
        self.extras_dir = os.path.join(home, 'extras')
        self.venvs_dir = os.path.join(home, 'venvs')
        self.download_dir = os.path.join(home, 'Downloads')

    def easy_joiner(self, parent: str, paths: Union[str, List[str]]) -> str:
        """Provides an easy way to join a path"""
        if isinstance(paths, str):
            paths = [paths]
        return self.pth.join(parent, *paths)

    def get_extension(self, path: str) -> str:
        """Gets the file extension of a path"""
        return self.pth.splitext(path)[1]

    def exists(self, path: str) -> bool:
        """Determines if the file exists"""
        return self.pth.exists(path)

    def get_files_in_dir(self, dir_path: str, full_paths: bool = False):
        """Retrieves all files in a particular directory, optionally returning their full paths"""
        pass
        # TODO this.
