import os
import re


def includes_extern(file: str, code: str):
    match = re.match(r'.*#\s*ifdef\s+__cplusplus\s+extern\s+"C"\s*{\s*#\s*endif', code, re.DOTALL)
    if match is None:
        return False
    return True


def check(root_dir: str, files: list):
    fails = []
    for f in files:
        with open(os.path.join(root_dir, f)) as codef:
            code = codef.read()
            if not includes_extern(f, code):
                fails.append(f)
    if len(fails) > 0:
        return ', '.join(fails)
    return None
