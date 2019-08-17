"""Setup kavalkilu.
Resources to build this:
    https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject
"""
import os
import re
from setuptools import setup, find_packages


here_dir = os.path.abspath(os.path.dirname(__file__))
init_fp = os.path.join(here_dir, *['kavalkilu', '__init__.py'])


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


version = find_x('version')

setup_args = {
    'name': 'kavalkilu',
    'version': version,
    'license': 'MIT',
    'description': 'A Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages(),
}

setup(**setup_args)
