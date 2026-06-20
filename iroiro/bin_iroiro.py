import argparse
import os
import sys

from os.path import basename, dirname
from pathlib import Path

from . import __version__
from . import bin


def main():
    prog = basename(sys.argv[0])
    sys.argv = sys.argv[1:]

    my_args = []
    remain_args = []

    dashing = True
    for arg in sys.argv:
        if arg.startswith('-') and dashing:
            my_args.append(arg)
        else:
            dashing = False
            remain_args.append(arg)

    sys.argv = remain_args

    recurse_depth = 0
    while sys.argv and sys.argv[0] == 'iroiro':
        recurse_depth += 1
        sys.argv.pop(0)

    if recurse_depth > 2:
        print(
r'''
        ╭────────────────────────────────╮
        │       ╭──────────────────────╮ │
        │       │   ╭────────────────╮ │ │
        │       │   │ RecursionError │ │ │
        │       │   ╰─────┬──────────╯ │ │
        │       │    .__. ╯            │ │
        │       │ .(=('')              │ │
        │       │  ||-||               │ │
        │       ╰────┬─────────────────╯ │
        │       ,__, ╯                   │
        │    ___(..)                     │
        │  /(   (__)                     │
        │ ' ||--||                       │
        ╰────────┬───────────────────────╯
            (__) ╯
    _______/(..)
  /(       /(__)
 * | w----||
   ||     ||
''', file=sys.stderr)
        sys.exit(1)

    if not sys.argv:
        for f in sorted(os.listdir(os.path.dirname(__file__))):
            if f.startswith('bin_') and f.endswith('.py'):
                m = os.path.splitext(f[4:])[0]
                print(m)
        sys.exit(1)

    subcmd = sys.argv[0]

    if subcmd == 'version':
        print(__version__)
        sys.exit()

    elif subcmd == 'path':
        print(Path(__file__).parent / 'bin')
        sys.exit()

    try:
        getattr(bin, subcmd).main()
    except (AttributeError, ModuleNotFoundError):
        print(f'Unknown subcommand: {subcmd}', file=sys.stderr)
        sys.exit(1)
