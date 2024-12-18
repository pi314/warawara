import sys
import shutil
import re

from . import lib_colors

from .lib_colors import paint
from .lib_colors import color
from .lib_regex import rere
from .lib_math import distribute


def main():
    prog = sys.argv[0]
    argv = sys.argv[1:]

    if not argv:
        print('Format: ESC[30;48;5;{}m')
        for c in range(0, 256):
            print(paint(fg=0, bg=c)(' ' + str(c).rjust(3)), end='')

            if c < 16 and (c + 1) % 8 == 0:
                print()

            if c >= 16 and (c - 16 + 1) % 36 == 0:
                print()

            if c in (15, 231):
                print()

        print()
        sys.exit()

    tiles = [[]]
    errors = []
    minus = 0
    for arg in argv:
        a = rere(arg)

        if a.match(r'^[0-9]+$'):
            tiles[-1].append((arg, color(int(arg, 10))))

        elif a.match(r'^#[0-9A-Fa-f]{6}$'):
            tiles[-1].append((arg, color(arg)))

        elif a.match(r'^[A-Za-z0-9]+$'):
            try:
                tiles[-1].append((arg, getattr(lib_colors, arg)))
            except AttributeError:
                errors[-1].append(arg)

        elif a.match(r'^-([0-9]+)$'):
            minus = int(a.group(1), 10)

        elif arg == '/':
            tiles.append([])

        else:
            errors.append(arg)

    if errors:
        for error in errors:
            print('Invalid color:', error)
        sys.exit(1)

    cols, lines = shutil.get_terminal_size()
    lines -= minus

    for idx in distribute(range(len(max(tiles, key=len))), lines):
        colors = list(filter(None, [(c[idx] if idx < len(c) else None) for c in tiles]))
        widths = []
        quo, rem = divmod(cols, len(colors))
        widths = [quo + (i < rem) for i, elem in enumerate(colors)]

        line = ''
        for idx, textcolor in enumerate(colors):
            text, c = textcolor
            line += paint(fg=c, bg=c)(text) + (~c)(' ' * (widths[idx] - len(text)))

        print(line)
