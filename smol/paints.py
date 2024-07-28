import re
import abc


__all__ = ['paint']
__all__ += ['nocolor', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'orange']
__all__ += ['decolor']
__all__ += ['color', 'color256', 'rgb', 'gradient']


def is_uint8(i):
    return isinstance(i, int) and 0 <= i < 256


def lerp(a, b, t):
    return ((1 - t) * a) + (t * b)


class Color(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def __repr__(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def __eq__(self, other):
        ...

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        ...


def color(*args, **kwargs):
    # unpack
    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        args = args[0]

    # copy ctor
    if len(args) == 1 and issubclass(type(args[0]), Color):
        return type(args[0])(*args, **kwargs)

    # color256 ctor
    elif len(args) == 1 and (args[0] is None or is_uint8(args[0])):
        return color256(*args, **kwargs)

    # rgb ctor
    elif len(args) == 3 and all(is_uint8(i) for i in args):
        return rgb(*args, **kwargs)

    # rgb ctor #xxxxxx
    elif len(args) == 1 and re.match(r'^#[0-9a-f]{6}$', args[0].lower()):
        return rgb(*args, **kwargs)

    raise TypeError('Invalid arguments')


class color256(Color):
    def __init__(self, code):
        if isinstance(code, self.__class__):
            code = code.code

        self.code = code

        if code is None:
            self.seq = ''
        elif is_uint8(code):
            self.seq = '5;{}'.format(self.code)
        else:
            raise TypeError('Invalid color code: {}'.format(code))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.code)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.code == other.code

    def __call__(self, prefix):
        if not self.seq:
            return ''
        return prefix + ';' + self.seq

    def __int__(self):
        return self.code


class rgb(Color):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], self.__class__):
            other = args[0]
            (self.r, self.g, self.b) = (other.r, other.g, other.b)
        elif len(args) == 1 and re.match(r'^#[0-9a-f]{6}$', args[0].lower()):
            rgb_str = args[0][1:]
            self.r = int(rgb_str[0:2], 16)
            self.g = int(rgb_str[2:4], 16)
            self.b = int(rgb_str[4:6], 16)
        elif len(args) == 3 and all(is_uint8(i) for i in args):
            (self.r, self.g, self.b) = args
        else:
            raise TypeError('Invalid rgb value: {}'.format(args))

        self.seq = '2;{};{};{}'.format(self.r, self.g, self.b)

    def __repr__(self):
        return 'rgb({}, {}, {})'.format(self.r, self.g, self.b)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and int(self) == int(other)

    def __call__(self, prefix):
        if not self.seq:
            return ''
        return prefix + ';' + self.seq

    def __int__(self):
        return (self.r << 16) | (self.g << 8) | (self.b)


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
    if not isinstance(A, Color) or not isinstance(B, Color):
        raise TypeError('Cannot calculate gradient() on non-Color objects')

    if N is not None and not isinstance(N, int):
        raise TypeError('N must be a integer')

    if N is not None and N < 2:
        raise ValueError('N={} is too small'.format(N))

    if N == 2:
        return (A, B)

    if not isinstance(A, color256) or not isinstance(B, color256):
        return (A, B)

    if A.code in range(232, 256) and B.code in range(232, 256):
        return gradient_color256_gray(A, B, N)

    if A.code in range(16, 232) and B.code in range(16, 232):
        def color_to_rgb6(p):
            c = int(p) - 16
            r = c // 36
            g = (c % 36) // 6
            b = c % 6
            return (r, g, b)

        def rgb6_to_color(rgb):
            return color256(rgb[0] * 36 + rgb[1] * 6 + rgb[2] + 16)

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


def gradient_color256_gray(A, B, N):
        a, b = A.code, B.code
        reverse = (b < a)
        if reverse:
            a, b = b, a
        n = (b + 1 - a)

        if N is None or N == n:
            ret = tuple(color256(c) for c in range(a, b + 1))

        if N < n:
            # Discrete averaging skipped colors to fit N
            skips = b - a + 1 - N
            step = skips // (N - 1) + 1
            ret = (color256(a),) + tuple(color256(a + (t * step)) for t in range(1, N-1)) + (color256(b),)

        if N > n:
            # Duplicate colors to match N
            ret = []
            dup, r = divmod(N, n)
            for i in range(a, b+1):
                for d in range(dup + (i < r + a)):
                    ret.append(color256(i))

        if reverse:
            ret = ret[::-1]

        return ret
