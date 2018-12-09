"""Setup kavalkilu.
Resources to build this:
    https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject
"""
import os
import re
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


setup_args = {
    'name': 'kavalkilu',
    'version': find_version(init_fp),
    'license': 'MIT',
    'description': 'A Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages()
}
setup(**setup_args)
