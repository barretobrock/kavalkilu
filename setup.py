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


def parse_reqs(file_prefix):
    """Takes in a requirements file (ending in *_requirements.frozen) in reqs/,
    parses a list of requirements"""
    fpath = os.path.join(here_dir, *['reqs', '{}_requirements.frozen'.format(file_prefix)])
    with open(fpath, 'r') as f:
        reqs_raw = f.read()
    reqs_list = reqs_raw.strip().split('\n')
    return reqs_list


# Package Requirements
packages = {
    'pi-only': parse_reqs('raspi_only'),
    'server-only': parse_reqs('server_only'),
    'all-platforms': parse_reqs('all_machines')
}

# Build out the installation requirements
install_packages = []
for k, v in packages.items():
    if k == 'pi-only':
        # Raspberry Pi Only packages
        install_packages += ['{};platform_machine=="arm" or platform_machine=="armv6l"'.format(x) for x in v]
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
    'packages': find_packages(exclude=['tests']),
    'dependency_links': [
        'https://github.com/barretobrock/slacktools/tarball/master#egg=slacktools'
    ],
    'install_requires': install_packages,
}

setup(**setup_args)
