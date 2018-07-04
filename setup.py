
from distutils.command.install import INSTALL_SCHEMES
from os.path import join, abspath, dirname
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
    'long_description': open(join(abspath(dirname(__file__)), "README.md")).read(),
    'url': 'https://github.com/barretobrock/kavalkilu',
    'package_dir': {
        'kavalkilu': 'kavalkilu',
        'kavalkilu.comm': 'kavalkilu/comm',
        'kavalkilu.sensors': 'kavalkilu/sensors',
        'kavalkilu.switches': 'kavalkilu/switches',
        'kavalkilu.tools': 'kavalkilu/tools'
    },
    'packages': [
        'kavalkilu',
        'kavalkilu.tools.date',
        'kavalkilu.tools.domoticz',
        'kavalkilu.tools.email',
        'kavalkilu.tools.gpio',
        'kavalkilu.tools.light',
        'kavalkilu.tools.log',
        'kavalkilu.tools.openhab',
        'kavalkilu.tools.path',
        'kavalkilu.tools.relay',
        'kavalkilu.tools.secure_copy',
        'kavalkilu.tools.selenium',
        'kavalkilu.tools.sensors',
    ],
    'include_package_data': True,
    'zip_safe': False
}
setup(**setup_args)
