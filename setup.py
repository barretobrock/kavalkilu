"""Setup kavalkilu.
Resources to build this:
    https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject

Notes:
    - Package requirements are stored in a list of dicts. Each item in the dict determines
        1) How the package will be installed (e.g., with pip or apt)
        2) Where the package is required (e.g., only on raspberry pi devices)

    - Where Types are determined on 1) hostname or 2) os.uname() info:
        - everywhere: all devices
        - raspberry_pi: only Raspberry Pi devices (os.uname()[4][:3] == 'arm')
        - non_raspi: only non-Raspberry Pi devices (os.uname()[4][:3] != 'arm')
        - server: only for device serving as home server (socket.gethostname() == 'homeserv')


"""
import os
import re
import sys
from datetime import datetime
from setuptools import setup, find_packages


here_dir = os.path.abspath(os.path.dirname(__file__))
init_fp = os.path.join(here_dir, '__init__.py')


def find_x(x='version', init_filepath=init_fp, return_str=True):
    with open(init_filepath, 'r') as f:
        txt = f.read()
    match = re.search(r"^__{}__ = ['\"]([^'\"]*)['\"]".format(x), txt, re.M)
    if match:
        if return_str:
            return match.group(1)
        else:
            return match, txt
    raise RuntimeError("Unable to find '__{}__' string.".format(x))


setup_args = {
    'name': 'kavalkilu',
    'version': find_x('version'),
    'license': 'MIT',
    'description': 'A Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages(),
}

setup(**setup_args)
