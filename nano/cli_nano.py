import sys

from os.path import basename

from . import cli_selftest
from . import cli_palette
from . import cli_sponge
from . import cli_ntfy


def main():
    prog = basename(sys.argv[0])
    argv = sys.argv[1:]

    if not argv:
        print(prog, argv)
        print('WIP')
        return 1

    if argv[0] == 'selftest':
        cli_selftest.main(argv[1:])

    if argv[0] in ('rainbow', 'palette'):
        cli_palette.main(argv[1:])

    if argv[0] in ('sponge',):
        cli_sponge.main(argv[1:])

    if argv[0] in ('ntfy',):
        cli_ntfy.main(argv[1:])
