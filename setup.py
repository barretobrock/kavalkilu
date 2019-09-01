"""Setup kavalkilu.
Resources to build this:
    https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject
"""
import os
import versioneer
from setuptools import setup, find_packages


here_dir = os.path.abspath(os.path.dirname(__file__))
init_fp = os.path.join(here_dir, *['kavalkilu', '__init__.py'])


setup_args = {
    'name': 'kavalkilu',
    'version': versioneer.get_version(),
    'cmdclass': versioneer.get_cmdclass(),
    'license': 'MIT',
    'description': 'A Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages(),
}

setup(**setup_args)
