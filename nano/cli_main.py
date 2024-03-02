import sys

from os.path import basename

from . import cli_selftest


def main():
    prog = basename(sys.argv[0])
    argv = sys.argv[1:]

    if argv and argv[0] == 'selftest':
        cli_selftest.main(argv[1:])

    else:
        print(prog, argv)
        print('WIP')
