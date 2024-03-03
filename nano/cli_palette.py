import sys

from . import lib_paint

from .lib_paint import paint


def main(argv):
    if not argv:
        print('Format: ESC[30;48;5;{}m')
        for color in range(0, 256):
            print(paint(fg=0, bg=color)(' ' + str(color).rjust(3)), end='')

            if color < 16 and (color + 1) % 8 == 0:
                print()

            if color >= 16 and (color - 16 + 1) % 36 == 0:
                print()

            if color in (15, 231):
                print()

        print()

    else:
        for arg in argv:
            print(
                    paint(fg=int(arg), bg=int(arg))(arg.rjust(3)) +
                    paint(bg=int(arg))(' ' * 100)
                    )


def cli_main():
    main(sys.argv[1:])
