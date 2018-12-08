"""Setup kavalkilu.
Resources to build this:
    https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject
"""
import os
import codecs
import re
from setuptools import setup, find_packages


setup_args = {
    'name': 'kavalkilu',
    'version': '0.2.2',
    'license': 'MIT',
    'description': 'A    Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages()
}
setup(**setup_args)
