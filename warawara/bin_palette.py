import sys

from . import lib_paints

from .lib_paints import paint


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
        for arg in argv:
            print(
                    paint(fg=int(arg), bg=int(arg))(arg.rjust(3)) +
                    paint(bg=int(arg))(' ' * 100)
                    )
