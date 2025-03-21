import glob
import os

from ditidy.error import on_error
from . import dir_name
from . import file_name
from . import include_guard
from . import extern_c


def process_patterns(root_dir: str, patterns: list):
    """
    Patern listesine göre path'leri bulur ve pathleri normalize eder.
    Ayrıca tekrarlayan pathleri filtreler.
    Pathler file ve directory olabilir.

    Eğer patternlerden birisi herhangi bir path'e eşleşmiyorsa hata verir.
    """
    paths = []
    for pattern in patterns:
        temp = glob.glob(pattern, root_dir=root_dir, recursive=True, include_hidden=True)
        if len(temp) == 0:
            on_error(f"no path(s) found in the pattern= {pattern}")
        paths.extend(temp)
    paths = [os.path.normpath(i) for i in paths]
    paths = list(set(paths))
    paths.sort()
    return paths


def files_from_paths(root_dir: str, paths: list):
    """
    Pathlerden file'ları elde eder.
    Eğer path file ise işlem yapılmaz.
    Eğer path directory ise bu directory altındaki tüm dosyalar recursive olarak bulunur ve path normalize edilir.
    Tekrarlanan file'lar filtrelenir.

    Eğer directorylerden birisi boşsa hata verir.
    """
    files = []
    for i in paths:
        if os.path.isfile(os.path.join(root_dir, i)):
            files.append(i)
        else:
            dir = os.path.join(i, "**")
            temp = glob.glob(dir, root_dir=root_dir, recursive=True, include_hidden=True)
            if len(temp) == 0:
                on_error(f"no file(s) found in the dir= {dir}")
            temp = [i for i in temp if os.path.isfile(os.path.join(root_dir, i))]
            temp = [os.path.normpath(i) for i in temp]
            files.extend(temp)
    files = list(set(files))
    files.sort()
    return files


def get_files(root_dir: str, includes: list, excludes: list):
    including_files = files_from_paths(root_dir, process_patterns(root_dir, includes))
    excluding_files = files_from_paths(root_dir, process_patterns(root_dir, excludes))
    files = list(set(including_files)-set(excluding_files))
    files.sort()
    if len(files) == 0:
        on_error("no file(s) left")
    return files


def get_dirs(root_dir: str, includes: list, excludes: list):
    including_dirs = [i for i in process_patterns(root_dir, includes) if os.path.isdir(os.path.join(root_dir, i))]
    including_dirs = [os.path.normpath(i) for i in including_dirs]
    excluding_dirs = [i for i in process_patterns(root_dir, excludes) if os.path.isdir(os.path.join(root_dir, i))]
    excluding_dirs = [os.path.normpath(i) for i in excluding_dirs]
    dirs = list(set(including_dirs)-set(excluding_dirs))
    dirs.sort()
    if len(dirs) == 0:
        on_error("no dir(s) left")
    return dirs


def checks(root_dir: str, config: dict):
    errors = []
    for c in config.keys():
        if c == "dir-name":
            dirs = get_dirs(root_dir, config.get(c)["includes"], config.get(c)["excludes"])
            error = dir_name.check(dirs)
            if error:
                errors.append(f"{c}: {error}")
        elif c == "file-name":
            files = get_files(root_dir, config.get(c)["includes"], config.get(c)["excludes"])
            error = file_name.check(files)
            if error:
                errors.append(f"{c}: {error}")
        elif c == "include-guard":
            files = get_files(root_dir, config.get(c)["includes"], config.get(c)["excludes"])
            error = include_guard.check(root_dir, files)
            if error:
                errors.append(f"{c}: {error}")
        elif c == "extern-c":
            files = get_files(root_dir, config.get(c)["includes"], config.get(c)["excludes"])
            error = extern_c.check(root_dir, files)
            if error:
                errors.append(f"{c}: {error}")
    if len(errors) > 0:
        on_error(os.linesep.join(errors))
