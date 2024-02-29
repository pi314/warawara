import sys

from os.path import basename


def main(prog=None, argv=[]):
    if prog is None and not argv:
        prog = basename(sys.argv[0])
        argv = sys.argv[1:]

    print(prog, argv)
    print('WIP')
