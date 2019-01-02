"""Setup kavalkilu.
Resources to build this:
    https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject

Notes:
    - Package requirements are stored in a list of dicts. Each item in the dict determines
        1) How the package will be installed (e.g., with pip or apt)
        2) Where the package is required (e.g., only on reaspberry pi devices)

    - Where Types are determined on 1) hostname or 2) os.uname() info:
        - everywhere: all devices
        - raspberry_pi: only Raspberry Pi devices (os.uname()[4][:3] == 'arm')
        - non_raspi: only non-Raspberry Pi devices (os.uname()[4][:3] != 'arm')
        - server: only for device serving as home server (socket.gethostname() == 'homeserv')


"""
import os
import re
import socket
from setuptools import setup, find_packages


here_dir = os.path.abspath(os.path.dirname(__file__))
init_fp = os.path.join(here_dir, '__init__.py')


def find_version(init_filepath):
    with open(init_filepath, 'r') as f:
        version_file_txt = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file_txt, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


pckgs = [
    {
        'pckg': 'sqlalchemy',
        'method': 'pip',
        'where': 'everywhere'
    }, {
        'pckg': 'python3-rpi.gpio',
        'method': 'apt',
        'where': 'raspberry_pi'
    }, {
        'pckg': 'phue',
        'method': 'pip',
        'where': 'everywhere'
    }, {
        'pckg': 'pushbullet.py',
        'method': 'pip',
        'where': 'everywhere'
    }, {
        'pckg': 'amcrest',
        'method': 'pip',
        'where': 'server'
    }, {
        'pckg': 'roku',
        'method': 'pip',
        'where': 'server'
    }, {
        'pckg': 'paramiko',
        'method': 'pip',
        'where': 'everywhere'
    }, {
        'pckg': 'selenium',
        'method': 'pip',
        'where': 'non_raspi'
    }, {
        'pckg': 'Adafruit_DHT',
        'method': 'pip',
        'where': 'raspberry_pi'
    }, {
        'pckg': 'python3-pandas',
        'method': 'apt',
        'where': 'everywhere'
    }
]

setup_args = {
    'name': 'kavalkilu',
    'version': find_version(init_fp),
    'license': 'MIT',
    'description': 'A Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages(),
}

# # Determine required packages
# pckgs_to_install = [pckg for pckg in pckgs if pckg['where'] == 'everywhere']
#
# dev = os.uname()[4][:3]
# if socket.gethostname() == 'homeserv':
#     # Server + everywhere + non_raspi
#     pckgs_to_install += [pckg for pckg in pckgs if pckg['where'] in ['server', 'non_raspi']]
# elif dev == 'arm':
#     # raspberry_pi + everywhere
#     pckgs_to_install += [pckg for pckg in pckgs if pckg['where'] in ['raspberry_pi']]
# else:
#     pckgs_to_install += [pckg for pckg in pckgs if pckg['where'] in ['non_raspi']]

setup(**setup_args)
