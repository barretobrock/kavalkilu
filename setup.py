
from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup
from setuptools.command.install import install

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


setup_args = {
    'cmdclass': {'install': install},
    'name': 'kavalkilu',
    'version': '0.2.1',
    'license': 'MIT',
    'description': 'A Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'packages': ['kavalkilu']
}
setup(**setup_args)
