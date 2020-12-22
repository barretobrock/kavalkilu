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

    def get_files_in_dir(self, dir_path: str, full_paths: bool = False, recursive: bool = False) -> List[str]:
        """Retrieves all files in a particular directory, optionally returning their full paths"""
        if recursive:
            return self._get_files_recursive(dir_path=dir_path, full_paths=full_paths)
        else:
            return self._get_files_non_recursive(dir_path=dir_path, full_paths=full_paths)

    @staticmethod
    def _get_files_non_recursive(dir_path: str, full_paths: bool = False) -> List[str]:
        """Retrieves only the files that are located at the directory input"""
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        if full_paths:
            return [os.path.join(dir_path, f) for f in files]
        return files

    @staticmethod
    def _get_files_recursive(dir_path: str, full_paths: bool = False) -> List[str]:
        """Retrieves all files at the given directory, including those in other directories "beneath" it"""
        files = []
        for dirpath, _, file_list in os.walk(dir_path):
            if full_paths:
                file_list = [os.path.join(dirpath, x) for x in file_list]
            files += file_list
        return files
