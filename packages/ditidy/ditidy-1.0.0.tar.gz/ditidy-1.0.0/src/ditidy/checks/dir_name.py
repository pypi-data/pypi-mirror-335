import re
import os

DIR_NAME_PATTERN = r'^[a-z0-9]+(_[a-z0-9]+)*$'


def check(dirs: list):
    fails = []
    for d in dirs:
        dir = os.path.basename(d)
        if re.match(DIR_NAME_PATTERN, dir) is None:
            fails.append(d)
    if len(fails) > 0:
        return ', '.join(fails)
    return None
