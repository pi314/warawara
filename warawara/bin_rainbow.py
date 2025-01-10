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
from .lib_math import is_uint8
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
    if is_uint8(arg):
        return color(arg)

    if not isinstance(arg, str):
        return

    if arg in lib_colors.names:
        return getattr(lib_colors, arg)

    m = rere(arg)

    # #RRGGBB format
    if m.fullmatch(r'#?([0-9a-fA-Z]{6})'):
        return color('#' + m.group(1))

    # @HHH,SSS,VVV format
    if m.fullmatch(r'@([0-9]+),([0-9]+),([0-9]+)'):
        return lib_colors.ColorHSV(arg)

    # int
    if m.fullmatch(r'[0-9]+'):
        try:
            i = int(arg, 10)
            if is_uint8(i):
                return color(i)
        except:
            return


def spell_suggestions(word):
    import difflib
    return difflib.get_close_matches(word, lib_colors.names, cutoff=0)


def spell_suggestion_err_msg(word):
    err_msg = 'Unknown color name "{}"'.format(word)
    suggestions = spell_suggestions(word)[:3]
    if suggestions:
        err_msg += ', did you mean '
        if len(suggestions) == 1:
            err_msg += '"{}"'.format(suggestions[0])
        elif len(suggestions) == 2:
            err_msg += '"{}", or "{}"'.format(suggestions[0], suggestions[1])
        elif len(suggestions) == 3:
            err_msg += '"{}", "{}", or "{}"'.format(*suggestions)
        err_msg += '?'
    add_error(err_msg)


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
    parser = argparse.ArgumentParser(
            prog=prog,
            description=('Query pre-defined colors from warawara, ' +
                         'or produce ' + colorful + ' strips/tiles to fill the screen.'),
            epilog=textwrap.dedent('''
                    Example usages:
                    $ {prog}
                    $ {prog} all
                    $ {prog} named --grep orange --hex
                    $ {prog} FFD700 --rgb
                    $ {prog} --tile --lines=2 --cols=8 salmon white
                    $ {prog} --gradient 00AFFF FFAF00
                    '''.strip('\n')).format(prog=prog),
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

    parser.add_argument('-r', '--reverse',
                        action='store_true',
                        help='''Reverse the output sequence''')

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

    parser.add_argument('-g', '--gradient',
                        action='store_true',
                        help='''Calculate color gradient for specified two colors
Ignores "all" and "named" macros''')

    parser.add_argument('-c', '--clockwise',
                        action=YesNoToBoolOption, nargs='?', choices=['yes', 'no'], const='yes',
                        help='''Calculate clockwise color gradient for HSV''')

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

    if args.tile and args.gradient:
        print('--tile and --gradient cannot be used together')
        sys.exit(1)

    elif args.tile:
        main_tile(args)

    else:
        main_list(args)


def main_list(args):
    if args.gradient:
        if not args.targets:
            print('No colors to gradient')
            sys.exit(1)

        if len(args.targets) == 1:
            print('Need destination color')
            sys.exit(1)

        if len(args.targets) > 3:
            print('Too many arguments')
            sys.exit(1)

        arg_src = args.targets[0]
        arg_dst = args.targets[1]

        if len(args.targets) == 3:
            arg_n = args.targets[2]
        else:
            arg_n = None

        src = parse_target(arg_src)
        if not src:
            spell_suggestion_err_msg(arg_src)

        dst = parse_target(arg_dst)
        if not dst:
            spell_suggestion_err_msg(arg_dst)

        try:
            n = int(arg_n, 10) if arg_n else None
        except:
            add_error('Invalid number: {}'.format(arg_n))

        check_errors()

        def color_text(this_color):
            if isinstance(this_color, lib_colors.Color256):
                return str(this_color.index)
            elif isinstance(this_color, lib_colors.ColorRGB):
                return '{:#X}'.format(this_color)
            elif isinstance(this_color, lib_colors.ColorHSV):
                return '@{:},{:},{:}'.format(this_color.H, this_color.S, this_color.V)
            else:
                line.append('(?)')

        expanded = [(g, color_text(g)) for g in lib_colors.gradient(src, dst, n, reverse=args.reverse, clockwise=args.clockwise)]

    else:
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
                spell_suggestion_err_msg(arg)

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
        expanded.sort(key=lambda x: (x[0].to_rgb() if isinstance(x[0], lib_colors.Color256) else x[0]).rgb)
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
        if not args.gradient and m.fullmatch(r'[0-9]+') and not m.fullmatch(r'#?[0-9a-fA-F]{6}'):
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
                line.append('({:>3}, {:>3}, {:>3})'.format(*rgb.RGB))

            elif val_fmt == 'hex':
                line.append('{:#X}'.format(rgb))

            elif val_fmt == 'hsv':
                line.append('(@{:>3}, {:>3}%, {:>3}%)'.format(*hsv.HSV))

        line.append(paint(fg=this_color, bg=this_color)('warawara'))

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
            if token in ('all', 'named'):
                add_error('"{}" cannot be used in tile mode'.format(token))
                continue

            t = parse_target(token)
            if t:
                tiles[-1].append((token, t))
            else:
                spell_suggestion_err_msg(token)

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

        if args.lines:
            print(line)
        else:
            print(line, end='\n' if not is_last else '')

    sys.stdout.flush()

    if not args.lines:
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
