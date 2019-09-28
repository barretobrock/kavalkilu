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

# Package Requirements
packages = {
    'pi-only': [
        'Adafruit_DHT',
        'picamera',
        'rpi-rf'
    ],
    'server-only': [
        'daemonize',
        'markovify',
        'image_slicer',
        'versioneer'
    ],
    'all-platforms': [
        'amcrest',
        'beautifulsoup4',
        'paramiko',
        'phue',
        'Pillow',
        'psutil',
        'pushbullet.py',
        'roku',
        'selenium',
        'slackclient==1.3.1',
        'sqlalchemy',
        'tabulate',
        'pytest'
    ]
}

# Build out the installation requirements
install_packages = []
for k, v in packages.items():
    if k == 'pi-only':
        # Raspberry Pi Only packages
        install_packages += ['{};platform_machine=="arm"'.format(x) for x in v]
    elif k == 'server-only':
        # Laptop / Server / Dev environment only packages
        install_packages += ['{};platform_machine=="x86_64"'.format(x) for x in v]
    else:
        install_packages += v

setup_args = {
    'name': 'kavalkilu',
    'version': versioneer.get_version(),
    'cmdclass': versioneer.get_cmdclass(),
    'license': 'MIT',
    'description': 'A Library for Integrating Home Automation Components',
    'url': 'https://github.com/barretobrock/kavalkilu',
    'author': 'Barret Obrock',
    'author_email': 'barret@barretobrock.ee',
    'packages': find_packages('kavalkilu', exclude=['tests']),
    'install_requires': install_packages
}

setup(**setup_args)
