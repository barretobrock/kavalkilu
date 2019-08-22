import os
import re
import sys
from datetime import datetime

here_dir = os.path.abspath(os.path.dirname(__file__))
init_fp = os.path.join(here_dir, *['kavalkilu', 'kavalkilu', '__init__.py'])


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


def write_x(x, new_val, init_filepath=init_fp):
    """Overwrites x (version or update_date) with new value and writes to file"""
    match, txt = find_x(x, init_filepath, return_str=False)

    front_slice = txt[:match.start()+len('__{}__ = "'.format(x))]
    end_slice = txt[match.end() - 1:]
    txt = '{}{}{}'.format(front_slice, new_val, end_slice)

    with open(init_filepath, 'w') as f:
        f.write(txt)


def increment_version(size):
    """Increments the version based on the size of the change.
    Default is path
    """
    cur_version = find_x('version')
    major, minor, patch = cur_version.split('.')
    if size == 'major':
        major = int(major) + 1
        minor = patch = 0
    elif size == 'minor':
        minor = int(minor) + 1
        patch = 0
    else:
        # Patch only
        patch = int(patch) + 1

    return '.'.join([str(x) for x in [major, minor, patch]])


ver_chg = None
# Version incrementing
if '--major' in sys.argv:
    # Major change occurred
    ver_chg = increment_version('major')
elif '--minor' in sys.argv:
    # Minor change occurred
    ver_chg = increment_version('minor')
else:
    # Patch change occurred
    ver_chg = increment_version('patch')

if ver_chg is not None:
    print('Writing new version: {}'.format(ver_chg))
    write_x('version', ver_chg)
    print('Updating update_date: {:%F}'.format(datetime.today()))
    write_x('update_date', datetime.today().strftime('%F'))

print(ver_chg)
