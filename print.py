import sys


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
