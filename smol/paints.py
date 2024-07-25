import re


__all__ = ['paint']
__all__ += ['nocolor', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'orange']
__all__ += ['decolor']
__all__ += ['color', 'gradient']


class color:
    def __init__(self, code):
        def is_uint8(i):
            return isinstance(i, int) and 0 <= i and i < 256

        if isinstance(code, self.__class__):
            code = code.code

        self.space = None
        self.code = None

        if code is None:
            self.space = None
            self.code = ''

        elif isinstance(code, str):
            self.space = None
            self.code = code

        elif isinstance(code, int):
            if is_uint8(code):
                self.space = 1
            else:
                raise TypeError('Color code exceeds range(0, 256): {}'.format(code))
            self.code = code

        elif isinstance(code, (tuple, list)):
            if len(code) != 3:
                raise TypeError('Invalid dimension: {}'.format(code))
            if not all(is_uint8(i) for i in code):
                raise TypeError('Color code exceeds range(0, 256): {}'.format(code))
            self.space = 3
            self.r = code[0]
            self.g = code[1]
            self.b = code[2]

        else:
            raise TypeError('Invalid color code: {}'.format(code))

        if not self.code:
            self.seq = ''
        if self.space is None:
            self.seq = self.code
        elif self.space == 1:
            self.seq = '5;{}'.format(self.code)
        elif self.space == 3:
            self.seq = '2;{};{};{}'.format(self.r, self.g, self.b)

    def __int__(self):
        if self.space == 1:
            return self.code
        if self.space == 3:
            return (self.r << 16) | (self.g << 8) | (self.b)

    def __call__(self, prefix):
        if not self.seq:
            return ''
        return prefix + ';' + self.seq

    def __repr__(self):
        if self.space == 1:
            return 'color(' + str(self.code) + ')'
        elif self.space == 3:
            return 'color({},{},{})'.format(*self.code)
        return 'color(code={})'.format(self.code)


class paint:
    def __init__(self, fg=None, bg=None):
        self.fg = color(fg)
        self.bg = color(bg)

        seq = ';'.join(filter(None, [self.fg('38'), self.bg('48')]))
        self.seq = '' if not seq else ('\033[' + seq + 'm')

    def __repr__(self):
        return 'paint(fg={fg}, bg={bg})'.format(fg=self.fg, bg=self.bg)

    def __call__(self, s=''):
        return s if not self.seq else f'{self.seq}{s}\033[m'

    def __str__(self):
        return self.seq or '\033[m'

    def __or__(self, other):
        fg = other.fg if other.fg.seq else self.fg
        bg = other.bg if other.bg.seq else self.bg

        return paint(fg=fg, bg=bg)

    def __add__(self, other):
        return self | other

    def __truediv__(self, other):
        return paint(fg=self.fg, bg=other.fg)

    def __invert__(self):
        return paint(fg=self.bg, bg=self.fg)

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


decolor_regex = re.compile('\033' + r'\[[\d;]*m')
def decolor(s):
    return decolor_regex.sub('', s)


def gradient(A, B, N=None):
    if isinstance(N, int) and N < 2:
        N = 2

    if not isinstance(A, color) or not isinstance(B, color):
        return tuple()

    if A.space != 1 or B.space != 1:
        return (A, B)

    if A.code in range(232, 256) and B.code in range(232, 256):
        return tuple(paint(c) for c in range(A.code, B.code + 1))

    if A.code in range(16, 232) and B.code in range(16, 232):
        def color_to_rgb6(p):
            c = int(p) - 16
            r = c // 36
            g = (c % 36) // 6
            b = c % 6
            return (r, g, b)

        def rgb6_to_color(rgb):
            return color(rgb[0] * 36 + rgb[1] * 6 + rgb[2] + 16)

        def rgb_add(a, b):
            return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

        rgb_a = color_to_rgb6(A)
        rgb_b = color_to_rgb6(B)

        if N == 3:
            return (A, rgb6_to_color(tuple(((rgb_a[i] + rgb_b[i]) // 2) for i in (0, 1, 2))), B)

        delta = tuple(rgb_b[i] - rgb_a[i] for i in (0, 1, 2))
        # print('delta', delta)

        def sgn(i):
            return (i > 0) - (i < 0)

        steps = []
        for n in range(max(map(abs, delta))):
            steps.append(tuple(sgn(delta[i]) for i in (0, 1, 2)))
            delta = tuple(delta[i] - sgn(delta[i]) for i in (0, 1, 2))

        acc = [rgb_a]
        for step in steps:
            acc.append(rgb_add(acc[-1], step))

        if N is None:
            ret = acc
        else:
            dup, r = divmod(N, len(acc))
            ret = []
            for i in range(len(acc)):
                for d in range(dup + (i < r)):
                    ret.append(acc[i])

        return tuple(rgb6_to_color(i) for i in ret)

    return (A, B)
