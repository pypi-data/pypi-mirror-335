import sys


def on_error(message: str):
    print(message, file=sys.stderr)
    exit(1)
