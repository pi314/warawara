import sys
import shutil
import argparse
import textwrap

from os.path import basename

from . import lib_colors

from .lib_colors import paint
from .lib_colors import color
from .lib_regex import rere
from .lib_math import distribute
from .lib_itertools import lookahead


errors = []
def add_error(errmsg):
    errors.append(errmsg)


def check_errors():
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)


def high_contrast_fg(c):
    if isinstance(c, lib_colors.Color256):
        c = c.index

    if c == 0:
        return None

    if c < 16:
        return 0

    elif c < 232:
        base = c - 16
        r = (base // 36)
        g = ((base % 36) // 6)
        b = (base % 6)

        if r < 2 and g < 2:
            return None

        if r < 3 and g < 1:
            return None

    elif c in range(232, 240):
        return None

    return 0


def parse_target(arg):
    if isinstance(arg, int) and 0 <= arg < 256:
        return color(arg)

    m = rere(arg)

    if m.fullmatch(r'#?[0-9a-fA-Z]{6}'):
        return color('#' + arg)

    if m.fullmatch(r'@([0-9]+),([0-9]+),([0-9]+)'):
        return lib_colors.ColorHSV(arg)

    if m.fullmatch(r'[0-9]+'):
        return color(int(arg))

    if isinstance(arg, str) and hasattr(lib_colors, arg):
        return getattr(lib_colors, arg)


def main_256cube():
    # Print color cube palette
    print('Format: ESC[30;48;5;{}m')
    for c in range(0, 256):
        color_rgb = color(c).to_rgb()
        print(paint(fg=high_contrast_fg(c), bg=c)(' ' + str(c).rjust(3)), end='')

        if c < 16 and (c + 1) % 8 == 0:
            print()
        if c >= 16 and (c - 16 + 1) % 36 == 0:
            print()
        if c in (15, 231):
            print()

    print()
    sys.exit()


def main():
    prog = basename(sys.argv[0])
    argv = sys.argv[1:]

    if not argv:
        main_256cube()

    colorful = ''.join(
            map(
                lambda x: lib_colors.color(x[0])(x[1]),
                zip(
                    ['#FF0000', '#FFC000', '#FFFF00',
                     '#C0FF00', '#00FF00', '#00FFC0',
                     '#00FFFF', '#00C0FF', '#3333FF', '#C000FF', '#FF00FF'],
                    'coooolorful'
                    )
                )
            )
    parser = argparse.ArgumentParser(prog=prog,
                                     description=('Query pre-defined colors from warawara, ' +
                                                  'or produce ' + colorful + ' strips/tiles to fill the screen.'),
                                     epilog=textwrap.dedent('''\
                                             Example usages:
                                             $ {prog}
                                             $ {prog} all
                                             $ {prog} named --grep orange --hex
                                             $ {prog} FFD700 --rgb
                                             $ {prog} --tile --lines=2 --cols=8 salmon white
                                     ''').format(prog=prog),
                                     allow_abbrev=False, add_help=False,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    parser.add_argument('--grep',
                        action='append',
                        help='''Filter out colors that does not contain the specified sub-string
This argument can be specified multiple times for multiple keywords''')

    parser.add_argument('-a', '--aliases',
                        action='store_true',
                        help='Show aliases of specified colors')

    parser.add_argument('--hex', dest='val_fmt',
                        action='append_const', const='hex',
                        help='Show RGB value in hex number')

    parser.add_argument('--rgb', dest='val_fmt',
                        action='append_const', const='rgb',
                        help='Show RGB value in 3-tuple')

    parser.add_argument('--hsv', dest='val_fmt',
                        action='append_const', const='hsv',
                        help='Show HSV value in 3-tuple')

    parser.add_argument('--sort',
                        nargs='?', choices=['index', 'name', 'rgb', 'hue', 'no'], const='index',
                        default='no',
                        help='Sort the output by the specified attribute')

    class YesNoToBoolOption(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values == 'yes')
    parser.add_argument('-m', '--merge',
                        action=YesNoToBoolOption, nargs='?', choices=['yes', 'no'], const='yes',
                        help='Merge colors that have same index')

    parser.add_argument('-M', '--no-merge',
                        action='store_false', dest='merge',
                        help='Dont merge colors that have same index')

    parser.add_argument('-t', '--tile',
                        action='store_true',
                        help='''Tiles to fill the whole screen
Ignores every other optional arguments except for --height and --width
Ignores "all" and "named" macros''')

    parser.add_argument('--cols', '--columns',
                        type=int,
                        help='Specify terminal columns')

    parser.add_argument('--lines',
                        type=int,
                        help='Specify terminal height')

    parser.add_argument('targets', nargs='*', help='''Names / indexs / RGB hex values / HSV values to query
"all" and "named" macros could be used in "list" mode''')

    parser.set_defaults(val_fmt=[])

    args = parser.parse_intermixed_args()
    # print(args)
    # exit()

    if args.tile:
        main_tile(args)
    else:
        main_list(args)


def main_list(args):
    if args.merge is None:
        if 'all' in args.targets or 'named' in args.targets:
            args.merge = True
        elif args.aliases:
            args.merge = True
        else:
            args.merge = False

    if args.grep and not args.targets:
        args.targets = ['all']

    expanded = []
    for arg in args.targets:
        if arg in ('all', 'named'):
            local_expansion = []
            if arg == 'all':
                for i in range(256):
                    local_expansion.append((parse_target(str(i)), []))

                for name in lib_colors.names:
                    c = parse_target(name)
                    local_expansion[c.index][1].append(name)

            elif arg == 'named':
                for name in lib_colors.names:
                    local_expansion.append((parse_target(name), [name]))

            for entry in local_expansion:
                if not entry[1]:
                    expanded.append((entry[0], None))
                else:
                    for name in entry[1]:
                        expanded.append((entry[0], name))

            del local_expansion
            continue

        t = parse_target(arg)
        if t:
            expanded.append((t, arg))
        else:
            add_error('Invalid color name "{}"'.format(arg))

    check_errors()

    # Grep
    if args.grep:
        for keyword in args.grep:
            tmp, expanded = expanded, []
            for C, name in tmp:
                if keyword == '':
                    if not name:
                        expanded.append((C, name))
                else:
                    if name and keyword in name:
                        expanded.append((C, name))
            del tmp

    # Sort
    if args.sort == 'index':
        expanded.sort(key=lambda x: int(x[0]) + (isinstance(x[0], lib_colors.ColorRGB) << 8))
    elif args.sort == 'name':
        expanded.sort(key=lambda x: ((isinstance(x[0], lib_colors.ColorRGB)), x[1]))
    elif args.sort == 'rgb':
        expanded.sort(key=lambda x: (x[0] if isinstance(x[0], lib_colors.Color256) else x[0]).to_rgb().rgb)
    elif args.sort == 'hue':
        def to_hsv(x):
            if isinstance(x, lib_colors.ColorHSV):
                return x
            if isinstance(x, lib_colors.ColorRGB):
                return x.to_hsv()
            if isinstance(x, lib_colors.Color256):
                return x.to_rgb().to_hsv()
        expanded.sort(key=lambda x: to_hsv(x[0]).h)

    inventory = []
    def stage(color, name):
        if name is None:
            name = ''

        m = rere(name)
        if m.fullmatch(r'[0-9]+') and not m.fullmatch(r'#?[0-9a-fA-F]{6}'):
            name = ''

        if not args.merge:
            inventory.append((color, [name] if name else []))
            return

        entries = filter(lambda entry: entry[0] == color, inventory)

        try:
            entry = next(entries)
            append = False
            if not entry[1]:
                append = True
            if name and args.merge and name not in entry[1]:
                append = True

            if append:
                entry[1].append(name)

            return

        except StopIteration:
            pass

        inventory.append((color, [name] if name else []))

    for entry in expanded:
        stage(entry[0], entry[1])

    if not inventory:
        print('No colors to query')
        sys.exit(1)

    unmentioned_names = set(lib_colors.names)
    for _, names in inventory:
        unmentioned_names -= set(names)

    aliases = [[] for i in range(256)]
    if args.aliases:
        for name in unmentioned_names:
            c = getattr(lib_colors, name).index
            aliases[c].append(name)

    for this_color, names in inventory:
        line = []
        rgb = this_color if isinstance(this_color, lib_colors.ColorRGB) else this_color.to_rgb()
        hsv = rgb.to_hsv()

        if isinstance(this_color, lib_colors.Color256):
            line.append('{:>3}'.format(this_color.index))
        elif isinstance(this_color, lib_colors.ColorRGB):
            line.append('(#)')
        elif isinstance(this_color, lib_colors.ColorHSV):
            line.append('(@)')
        else:
            line.append('(?)')

        for val_fmt in args.val_fmt:
            if val_fmt == 'rgb':
                line.append('(' + ','.join(map(lambda x: str(x).rjust(3), rgb.rgb)) + ')')

            elif val_fmt == 'hex':
                line.append('{:#X}'.format(rgb))

            elif val_fmt == 'hsv':
                line.append('(@{:>3}, {:>3}%, {:>3}%)'.format(int(hsv.h), int(hsv.s), int(hsv.v)))

        if args.val_fmt:
            line.append(paint(fg=this_color, bg=this_color)('warawara'))
        else:
            line.append(paint(fg=this_color, bg=this_color)('{:#X}'.format(rgb)))

        line.append(', '.join(names))

        if isinstance(this_color, lib_colors.Color256):
            aliases[this_color.index] = [name
                                         for name in aliases[this_color.index]
                                         if name not in names]
            if aliases[this_color.index]:
                a = ('(' + ', '.join(aliases[this_color.index]) + ')')
                line[-1] = line[-1] + (' ' if line[-1] else '') + a
                aliases[this_color.index] = []

        print(' '.join(line))


def main_tile(args):
    if not args.targets:
        print('No colors to tile')
        sys.exit(1)

    tiles = [[]]
    for arg in args.targets:
        for token in arg.split('/'):
            m = rere(token)

            if m.fullmatch(r'[0-9]+'):
                tiles[-1].append((token, color(int(token, 10))))

            elif m.fullmatch(r'#?[0-9A-Fa-f]{6}'):
                tiles[-1].append((token, color(token)))

            if m.fullmatch(r'@([0-9]+),([0-9]+),([0-9]+)'):
                tiles[-1].append((token, lib_colors.ColorHSV(token)))

            elif m.fullmatch(r'[A-Za-z0-9]+'):
                try:
                    tiles[-1].append((token, getattr(lib_colors, token)))
                except AttributeError:
                    add_error('Invalid color name "{}"'.format(token))

            else:
                add_error('Invalid color "{}"'.format(token))

        tiles.append([])

    check_errors()
    if not tiles[-1]:
        tiles.pop()

    cols, lines = shutil.get_terminal_size()
    cols = args.cols or cols
    lines = args.lines or lines

    if lines < 0:
        lines = len(tiles)

    for idx, is_last in lookahead(distribute(range(len(tiles)), lines)):
        colors = tiles[idx]
        widths = []
        quo, rem = divmod(cols, len(colors))
        widths = [quo + (i < rem) for i, elem in enumerate(colors)]
        line = ''
        for idx, textcolor in enumerate(colors):
            text, c = textcolor
            text = text[:widths[idx]]
            line += paint(fg=c, bg=c)(text) + (~c)(' ' * (widths[idx] - len(text)))

        print(line, end='\n' if not is_last else '')

    sys.stdout.flush()

    import termios, tty
    import os
    import select

    fd = sys.stdin.fileno()
    orig_term_attr = termios.tcgetattr(fd)
    when = termios.TCSADRAIN

    try:
        tty.setraw(fd, when=when)
        select.select([fd], [], [], None)[0]

    finally:
        print('\r\n')
        termios.tcsetattr(fd, when, orig_term_attr)
