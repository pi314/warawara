import os
import sys

from os.path import basename

from . import bin


def main():
    prog = basename(sys.argv[0])
    sys.argv = sys.argv[1:]

    if not sys.argv:
        for f in os.listdir(os.path.dirname(__file__)):
            if f.startswith('bin_') and f.endswith('.py'):
                m = os.path.splitext(f[4:])[0]
                print(m)
        sys.exit(1)

    subcmd = sys.argv[0]

    try:
        getattr(bin, subcmd).main()
    except AttributeError:
        print(f'Unknown subcommand: {subcmd}', file=sys.stderr)
        sys.exit(1)
    except ModuleNotFoundError:
        print(f'Unknown subcommand: {subcmd}', file=sys.stderr)
        sys.exit(1)
