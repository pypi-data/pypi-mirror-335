from typing import List
import yaml
import os

import yaml.scanner

from ditidy.error import on_error


CHECKS = ["dir-name", "file-name", "include-guard", "extern-c"]


def update_check_list(check_list: List[str], new_list: List[str], add: bool):
    for item in new_list:
        if item in check_list:
            check_list.remove(item)
    if add:
        check_list.extend(new_list)


def load_check_list(checks: any):
    check_list = []
    if not isinstance(checks, list):
        on_error("checks field should be list")
    for check_item in checks:
        if not isinstance(check_item, str):
            on_error(f"{check_item} field should be string")
        add = True
        if check_item.startswith("-"):
            add = False
        check = check_item.lstrip("-")
        if check == "*":
            update_check_list(check_list, CHECKS, add)
        elif check in CHECKS:
            update_check_list(check_list, [check], add)
        else:
            on_error(f"unknown check= {check}")
    return check_list


def load_glob_patterns(data: any):
    patterns = []
    if not isinstance(data, list):
        on_error("glob patterns should be a list")
    for pattern in data:
        if not isinstance(pattern, str):
            on_error("glob pattern should be a string")
        patterns.append(pattern)
    return patterns


def load_check_option(check_option_key: any, check_option: any):
    if check_option_key not in CHECKS:
        on_error(f"unknown check option key= {check_option_key}")
    elif not isinstance(check_option, dict):
        on_error(f"invalid check option= {check_option_key}")

    includes = load_glob_patterns(check_option.get("includes"))
    del check_option["includes"]

    excludes = []
    if check_option.get("excludes"):
        excludes = load_glob_patterns(check_option.get("excludes"))
        del check_option["excludes"]

    for key in check_option:
        on_error(f"unknown key in the check option {check_option_key}= {key}")

    return {"includes": includes, "excludes": excludes}


def load_check_options(check_options: any):
    options = {}
    if not isinstance(check_options, dict):
        on_error("check-options is invalid")
    for check_option_key in check_options.keys():
        option = load_check_option(check_option_key, check_options.get(check_option_key))
        options[check_option_key] = option
    return options


def load(data: any):
    if not isinstance(data, dict):
        on_error("invalid config file")

    check_list = load_check_list(data.get("checks"))
    del data["checks"]

    checks = load_check_options(data.get("check-options"))
    del data["check-options"]

    if len(data.keys()) > 0:
        on_error(f"unknown key(s)= {', '.join(data.keys())}")

    missing_options = list(set(check_list)-set(checks.keys()))
    if len(missing_options) > 0:
        on_error(f"missing check option(s)= {', '.join(missing_options)}")

    missing_checks = list(set(checks.keys())-set(check_list))
    if len(missing_checks) > 0:
        on_error(f"missing check(s)= {', '.join(missing_checks)}")

    return checks


def parse(file: str):
    if not os.path.exists(file) or not os.path.isfile(file):
        on_error("config file could not found")

    with open(file, "r") as config_file:
        try:
            data = yaml.safe_load(config_file)
        except yaml.scanner.ScannerError:
            on_error("invalid config file")
        return load(data)
