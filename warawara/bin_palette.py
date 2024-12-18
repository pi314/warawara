import sys
import shutil
import re

from . import lib_colors

from .lib_colors import paint
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

    else:
        colors = []
        errors = []
        minus = 0
        for arg in argv:
            a = rere(arg)

            if a.match(r'^[0-9]+$'):
                colors.append((arg, int(arg, 10)))

            elif a.match(r'^#[0-9A-Fa-f]{6}$'):
                colors.append((arg, arg))

            elif a.match(r'^[A-Za-z0-9]+$'):
                try:
                    colors.append((arg, getattr(lib_colors, arg)))
                except AttributeError:
                    errors.append(arg)
            elif a.match(r'^-([0-9]+)$'):
                minus = int(a.group(1), 10)
            else:
                errors.append(arg)

        if errors:
            for error in errors:
                print('Invalid color:', error)
            sys.exit(1)

        cols, lines = shutil.get_terminal_size()

        for text, color in distribute(colors, lines - minus):
            print(paint(fg=color, bg=color)(text) +
                  paint(bg=color)(' ' * (cols - len(text))))
