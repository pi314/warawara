class paint:
    def __init__(self, fg=None, bg=None, blue=None):
        if blue is not None:
            self.fg = (fg, bg, blue)
            self.bg = None
        else:
            self.fg = fg
            self.bg = bg

        fg_seq = self._seq(self.fg, True)
        bg_seq = self._seq(self.bg, False)
        seq = ';'.join(filter(None, [fg_seq, bg_seq]))
        self.seq = '' if not seq else ('\033[' + seq + 'm')

    def __repr__(self):
        return f'paint(fg={self.fg}, bg={self.bg})'

    def __call__(self, s=''):
        return '' if not self.seq else f'{self.seq}{s}\033[m'

    def __str__(self):
        return self.seq

    def __or__(self, other):
        fg = self.fg if other.fg is None else other.fg
        bg = self.bg if other.bg is None else other.bg
        return paint(fg=fg, bg=bg)

    def __add__(self, other):
        return self | other

    def __truediv__(self, other):
        return paint(fg=self.fg, bg=other.fg)

    def __rtruediv__(self, left):
        if left == 1:
            left = paint()

        return left | paint(fg=self.bg, bg=self.fg)

    def _seq(self, code, is_fg):
        if code in (None, ''):
            return ''

        if isinstance(code, str):
            return code

        ret = ('38' if is_fg else '48') + ';'

        if isinstance(code, int):
            ret += f'5;{code}'

        elif len(code) == 3:
            ret += '2;' + ';'.join(str(c) for c in code)

        else:
            raise ValueError(f'Invalid color code: {code}')

        return ret

    def __eq__(self, other):
        return self.seq == other.seq


nocolor = paint()
black = paint(0)
red = paint(1)
green = paint(2)
yellow = paint(3)
blue = paint(4)
magenta = paint(5)
cyan = paint(6)
white = paint(7)
orange = paint(208)


def selftest():
    color = lambda x: lambda s: f'\033[{x}m{s}\033[m'

    pass_tag = color(32)('[pass]')
    fail_tag = color(32)('[fail]')

    def hrepr(obj):
        if obj is None:
            return color(36)('None')

        if isinstance(obj, int):
            return color(35)(f'{obj}')

        if isinstance(obj, list):
            return '[' + ', '.join(hrepr(o) for o in obj) + ']'

        if isinstance(obj, dict):
            return '{' + ', '.join(hrepr(key) + ': ' + hrepr(value) for key, value in obj.items())+ '}'

        import re
        robj = repr(obj)

        if isinstance(obj, str):
            return color(35)(re.sub(
                r'(\\\w+)',
                r'\033[31m\1\033[35m',
                robj))

        # obj
        m = re.match(r'^(\w+)\((.*)\)$', robj)
        if m:
            import ast
            typename = m.group(1)
            arg_list = []
            for token in m.group(2).split(', '):
                if '=' in token:
                    a, b = token.split('=')
                    try:
                        b = ast.literal_eval(b)
                    except ValueError:
                        pass

                    arg_list.append(f'{a}={hrepr(b)}')

                else:
                    arg_list.append(token)

            return f'{typename}({", ".join(arg_list)})'

        return robj


    error_list = []

    import inspect
    def section(title):
        frame = inspect.stack()[1]
        filename = frame.filename
        lineno = frame.lineno
        print()
        print(color(36)(f'[section] {title} @({filename}:{lineno})'))

    def EXPECT_EQ(a, b):
        cond_repr = f'{hrepr(a)} == {hrepr(b)}'
        if a == b:
            print(pass_tag, cond_repr)
            return

        print(fail_tag, cond_repr)
        frame = inspect.stack()[1]
        error_list.append((frame, cond_repr))

    section('nocolor test')
    EXPECT_EQ(paint(), nocolor)
    EXPECT_EQ(nocolor(), '')

    section('fg test')
    EXPECT_EQ(black.seq,    '\033[38;5;0m')
    EXPECT_EQ(red.seq,      '\033[38;5;1m')
    EXPECT_EQ(green.seq,    '\033[38;5;2m')
    EXPECT_EQ(yellow.seq,   '\033[38;5;3m')
    EXPECT_EQ(blue.seq,     '\033[38;5;4m')
    EXPECT_EQ(magenta.seq,  '\033[38;5;5m')
    EXPECT_EQ(cyan.seq,     '\033[38;5;6m')
    EXPECT_EQ(white.seq,    '\033[38;5;7m')
    EXPECT_EQ(orange.seq,   '\033[38;5;208m')

    section('bg test')
    EXPECT_EQ(1 / red,      paint(bg=1))
    EXPECT_EQ(1 / green,    paint(bg=2))
    EXPECT_EQ(1 / yellow,   paint(bg=3))
    EXPECT_EQ(1 / blue,     paint(bg=4))
    EXPECT_EQ(1 / magenta,  paint(bg=5))
    EXPECT_EQ(1 / cyan,     paint(bg=6))
    EXPECT_EQ(1 / white,    paint(bg=7))
    EXPECT_EQ(1 / orange,   paint(bg=208))

    section('call test')
    EXPECT_EQ(black('color'),   '\033[38;5;0mcolor\033[m')
    EXPECT_EQ(red('color'),     '\033[38;5;1mcolor\033[m')
    EXPECT_EQ(green('color'),   '\033[38;5;2mcolor\033[m')
    EXPECT_EQ(yellow('color'),  '\033[38;5;3mcolor\033[m')
    EXPECT_EQ(blue('color'),    '\033[38;5;4mcolor\033[m')
    EXPECT_EQ(magenta('color'), '\033[38;5;5mcolor\033[m')
    EXPECT_EQ(cyan('color'),    '\033[38;5;6mcolor\033[m')
    EXPECT_EQ(white('color'),   '\033[38;5;7mcolor\033[m')
    EXPECT_EQ(orange('color'),  '\033[38;5;208mcolor\033[m')

    section('or test')
    EXPECT_EQ(black | (1 / yellow), paint(fg=0, bg=3))

    section('div test')
    ry = red / yellow
    EXPECT_EQ(ry, paint(fg=1, bg=3))
    EXPECT_EQ(ry.seq, '\033[38;5;1;48;5;3m')

    section('RGB test')
    EXPECT_EQ(paint(160, 90, 0)('test'), '\033[38;2;160;90;0mtest\033[m')

    for frame, cond_repr in error_list:
        print()
        print(fail_tag, cond_repr)
        print(f'    At {frame.filename}:{frame.lineno}')

    if error_list:
        print()
        print(fail_tag, f'{len(error_list)} errors')


selftest()
