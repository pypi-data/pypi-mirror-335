import os
import re


def guard_from_file(file: str):
    basename = os.path.basename(file)
    guard = re.sub(r'[^a-zA-Z0-9]', '_', basename)
    guard = guard.upper()
    return guard


def includes_guard(file: str, code: str):
    match = re.match(r'^\s*#\s*ifndef\s+([A-Za-z0-9_]+)\s+#\s*define\s+([A-Za-z0-9_]+).*#\s*endif\s*/\* ([A-Za-z0-9_]+) \*/\s*$', code, re.DOTALL)
    if match is None:
        return False
    if match.group(1) != guard_from_file(file) or match.group(1) != match.group(2) or match.group(2) != match.group(3):
        return False
    return True


def check(root_dir: str, files: list):
    fails = []
    for f in files:
        with open(os.path.join(root_dir, f), "r") as codef:
            code = codef.read()
            if not includes_guard(f, code):
                fails.append(f)
    if len(fails) > 0:
        return ', '.join(fails)
    return None
