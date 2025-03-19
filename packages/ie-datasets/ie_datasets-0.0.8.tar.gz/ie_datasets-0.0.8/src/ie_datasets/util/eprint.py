import sys


def eprint(*args, **kwargs):
    return print(*args, file=sys.stderr, **kwargs)
