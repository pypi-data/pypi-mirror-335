import re
import os

from .dir_name import DIR_NAME_PATTERN

FILE_NAME_PATTERN = DIR_NAME_PATTERN


def check(files: list):
    fails = []
    for f in files:
        dir = os.path.splitext(os.path.basename(f))[0]
        if re.match(FILE_NAME_PATTERN, dir) is None:
            fails.append(f)
    if len(fails) > 0:
        return ', '.join(fails)
    return None
