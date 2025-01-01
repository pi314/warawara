import sys
import shutil
import argparse

from os.path import basename

from . import lib_colors

from .lib_colors import paint
from .lib_colors import color
from .lib_regex import rere
from .lib_math import distribute
from .lib_math import is_uint8


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

    parser = argparse.ArgumentParser(description='rainbow', prog=prog, allow_abbrev=False)

    parser.add_argument('--grep',
                        action='append',
                        help='''List all colors defined by warawara that contains the specified sub-string.
                        Can be specified multiple times for multiple keywords''')

    parser.add_argument('-a', '--aliases',
                        action='store_true',
                        help='Show aliases of the specified color')

    parser.add_argument('--hex', dest='rgb_fmt',
                        action='append_const', const='hex',
                        help='Show RGB value in hex number')

    parser.add_argument('--rgb', dest='rgb_fmt',
                        action='append_const', const='rgb',
                        help='Show RGB value in 3-tuple')

    parser.add_argument('--sort',
                        nargs='?', choices=['index', 'name', 'rgb', 'hue', 'no'], const='index',
                        default='no',
                        help='Sort the output')

    class YesNoToBoolOption(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values == 'yes')
    parser.add_argument('-m', '--merge',
                        action=YesNoToBoolOption, nargs='?', choices=['yes', 'no'], const='yes',
                        help='Merge colors that have same index')

    parser.add_argument('-M', '--no-merge',
                        action='store_false', dest='merge',
                        help='Merge colors that have same index')

    parser.add_argument('-t', '--tile',
                        action='store_true',
                        help='Tiles to fill the whole screen; Ignores every other optional arguments')

    parser.add_argument('targets', nargs='*', help='''Names / indexs / RGB hex values to query.
                        "all" and "named" macros could be used in "list" mode''')

    parser.set_defaults(rgb_fmt=[])

    args = parser.parse_intermixed_args()

    if args.tile or '/' in args.targets:
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
        targets = ['all']

    errors = []

    expanded = []
    if args.targets:
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
                errors.append(arg)

        if errors:
            for error in errors:
                print('Invalid color name "{}"'.format(error))
            sys.exit(1)

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
        import colorsys
        expanded.sort(key=lambda x: colorsys.rgb_to_hsv(
            *map(
                lambda v: v / 255,
                (x[0] if isinstance(x[0], lib_colors.Color256) else x[0]).to_rgb().rgb)
            ))

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
        rgb = this_color.to_rgb() if isinstance(this_color, lib_colors.Color256) else this_color

        if isinstance(this_color, lib_colors.Color256):
            line.append('{:>3}'.format(this_color.index))
        else:
            line.append('(#)')

        for rgb_fmt in args.rgb_fmt:
            if rgb_fmt == 'rgb':
                line.append('(' + ','.join(map(lambda x: str(x).rjust(3), rgb.rgb)) + ')')

            elif rgb_fmt == 'hex':
                line.append('{:#X}'.format(rgb))

        if args.rgb_fmt:
            line.append(paint(fg=this_color, bg=this_color)('warawara'))
        else:
            if isinstance(this_color, lib_colors.Color256):
                line.append(paint(fg=this_color, bg=this_color)('{:#X}'.format(rgb)))
            else:
                line.append(paint(fg=this_color, bg=this_color)('{:#X}'.format(this_color)))

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
    errors = []
    for arg in args.targets:
        a = rere(arg)

        if a.match(r'^[0-9]+$'):
            tiles[-1].append((arg, color(int(arg, 10))))

        elif a.match(r'^#[0-9A-Fa-f]{6}$'):
            tiles[-1].append((arg, color(arg)))

        elif a.match(r'^[A-Za-z0-9]+$'):
            try:
                tiles[-1].append((arg, getattr(lib_colors, arg)))
            except AttributeError:
                errors.append(arg)

        elif arg == '/':
            tiles.append([])

        else:
            errors.append(arg)

    if errors:
        for error in errors:
            print('Invalid color:', error)
        sys.exit(1)

    cols, lines = shutil.get_terminal_size()

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

    try:
        input()
    except EOFError:
        pass
