import re
import abc
import itertools

from .lib_math import sgn
from .lib_math import vector
from .lib_math import lerp
from .lib_math import interval
from .lib_math import distribute
from .lib_math import is_uint8

from .lib_itertools import unwrap_one

from .internal_utils import exporter
export, __all__ = exporter()


@export
class Color(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs): # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self): # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def __int__(self): # pragma: no cover
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, self.__class__) and int(self) == int(other)

    def __call__(self, *args):
        return self.fg(*args)

    def fg(self, *args):
        return self.apply('38', ' '.join(str(arg) for arg in args))

    def bg(self, *args, **kwargs): # pragma: no cover
        return self.apply('48', ' '.join(str(arg) for arg in args))

    def apply(self, ground, s):
        if not self.seq:
            return s
        return '\033[{};{}m{}\033[m'.format(ground, self.seq, str(s))

    def __str__(self):
        return '\033[38;{}m'.format(self.seq) if self.seq else '\033[m'

    def __invert__(self):
        return ColorCompound(bg=self)

    def __truediv__(self, other):
        if not isinstance(other, Color):
            raise TypeError('Only Color() / Color() is allowed')
        return ColorCompound(fg=self, bg=other)

    def __or__(self, other):
        if isinstance(other, Color):
            return self if self.seq else other
        return ColorCompound(fg=self) | other


@export
def color(*args, **kwargs):
    args = unwrap_one(args)

    # empty
    if not args:
        return Color256(None)

    # copy ctor
    elif len(args) == 1 and issubclass(type(args[0]), Color):
        return type(args[0])(*args, **kwargs)

    # Color256 ctor
    elif len(args) == 1 and (args[0] is None or is_uint8(args[0])):
        return Color256(*args, **kwargs)

    # ColorRGB ctor
    elif len(args) == 3 and all(is_uint8(i) for i in args):
        return ColorRGB(*args, **kwargs)

    # ColorRGB ctor #xxxxxx
    elif len(args) == 1 and isinstance(args[0], str) and re.match(r'^#[0-9a-f]{6}$', args[0].lower()):
        return ColorRGB(*args, **kwargs)

    raise TypeError('Invalid arguments')


@export
class Color256(Color):
    def __init__(self, code=None):
        if isinstance(code, self.__class__):
            code = code.code

        self.code = code

        if code is None:
            self.seq = ''
        elif is_uint8(code):
            self.seq = '5;{}'.format(self.code)
        else:
            raise TypeError('Invalid color code: {}'.format(code))

    @property
    def rgb(self):
        if self.code < 16:
            base = 0xFF if (self.code > 7) else 0x80
            is_7 = (self.code == 7)
            is_8 = (self.code == 8)
            R = base * ((self.code & 0x1) != 0) + (0x40 * is_7) + (0x80 * is_8)
            G = base * ((self.code & 0x2) != 0) + (0x40 * is_7) + (0x80 * is_8)
            B = base * ((self.code & 0x4) != 0) + (0x40 * is_7) + (0x80 * is_8)

        elif self.code < 233:
            base = self.code - 16
            index_R = (base // 36)
            index_G = ((base % 36) // 6)
            index_B = (base % 6)
            R = (55 + index_R * 40) if index_R > 0 else 0
            G = (55 + index_G * 40) if index_G > 0 else 0
            B = (55 + index_B * 40) if index_B > 0 else 0

        else:
            R = G = B = (self.code - 232) * 10 + 8

        return (R, G, B)

    @property
    def r(self):
        return self.rgb[0]

    @property
    def g(self):
        return self.rgb[1]

    @property
    def b(self):
        return self.rgb[2]

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.code)

    def __int__(self):
        return self.code


@export
class ColorRGB(Color):
    def __init__(self, *args):
        args = unwrap_one(args)

        if not args:
            self.r = 0
            self.g = 0
            self.b = 0
            self.seq = ''
            return

        elif len(args) == 1 and isinstance(args[0], self.__class__):
            other = args[0]
            (self.r, self.g, self.b) = (other.r, other.g, other.b)

        elif len(args) == 1 and isinstance(args[0], str) and re.match(r'^#[0-9a-f]{6}$', args[0].lower()):
            rgb_str = args[0][1:]
            self.r = int(rgb_str[0:2], 16)
            self.g = int(rgb_str[2:4], 16)
            self.b = int(rgb_str[4:6], 16)

        elif len(args) == 3 and all(is_uint8(i) for i in args):
            (self.r, self.g, self.b) = args

        else:
            raise TypeError('Invalid RGB value: {}'.format(args))

        self.seq = '2;{};{};{}'.format(self.r, self.g, self.b)

    def __repr__(self):
        return 'ColorRGB({}, {}, {})'.format(self.r, self.g, self.b)

    def __int__(self):
        return (self.r << 16) | (self.g << 8) | (self.b)


@export
class ColorCompound:
    def __init__(self, fg=None, bg=None):
        self.fg = color(fg)
        self.bg = color(bg)

        seq = ';'.join(filter(None, [
            '38;' + self.fg.seq if self.fg.seq else None,
            '48;' + self.bg.seq if self.bg.seq else None,
            ]))
        self.seq = '' if not seq else ('\033[' + seq + 'm')

    def __repr__(self):
        return 'ColorCompound(fg={fg}, bg={bg})'.format(fg=self.fg, bg=self.bg)

    def __call__(self, s=''):
        return s if not self.seq else f'{self.seq}{s}\033[m'

    def __str__(self):
        return self.seq or '\033[m'

    def __or__(self, other):
        fg = other.fg if other.fg.seq else self.fg
        bg = other.bg if other.bg.seq else self.bg

        return ColorCompound(fg=fg, bg=bg)

    def __truediv__(self, other):
        return ColorCompound(fg=self.fg, bg=other.fg)

    def __invert__(self):
        return ColorCompound(fg=self.bg, bg=self.fg)

    def __eq__(self, other):
        return self.seq == other.seq

export('paint')
paint = ColorCompound


export('nocolor', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'orange')
nocolor = color()
black = color(0)
red = color(1)
green = color(2)
yellow = color(3)
blue = color(4)
magenta = color(5)
cyan = color(6)
white = color(7)
orange = color(208)


decolor_regex = re.compile('\033' + r'\[[\d;]*m')

@export
def decolor(s):
    return decolor_regex.sub('', s)


@export
def gradient(A, B, N=None):
    if not isinstance(A, Color) or not isinstance(B, Color):
        raise TypeError('Can only calculate gradient() on Color objects')

    if N is not None and not isinstance(N, int):
        raise TypeError('N must be a integer')

    if N is not None and N < 2:
        raise ValueError('N={} is too small'.format(N))

    if N == 2:
        return (A, B)

    if isinstance(A, Color256) and isinstance(B, Color256):
        return gradient_color256(A, B, N=N)

    if isinstance(A, ColorRGB) and isinstance(B, ColorRGB):
        return gradient_rgb(A, B, N=N)

    return (A, B)


def gradient_color256(A, B, N=None):
    if A.code in range(232, 256) and B.code in range(232, 256):
        return gradient_color256_gray(A, B, N)

    if A.code in range(16, 232) and B.code in range(16, 232):
        return gradient_color256_rgb(A, B, N)

    return (A, B)


def gradient_color256_gray(A, B, N=None):
    a, b = A.code, B.code
    direction = sgn(b - a)
    n = abs(b - a) + 1
    return tuple(Color256(c) for c in distribute(interval(a, b), N or n))


def gradient_color256_rgb(A, B, N=None):
    def color_to_rgb6(p):
        c = int(p) - 16
        r = c // 36
        g = (c % 36) // 6
        b = c % 6
        return vector(r, g, b)

    def rgb6_to_color(rgb6):
        return Color256(rgb6[0] * 36 + rgb6[1] * 6 + rgb6[2] + 16)

    rgb_a = color_to_rgb6(A)
    rgb_b = color_to_rgb6(B)

    delta = rgb_b - rgb_a
    cont_step_count = max(abs(d) for d in delta)

    if N is None or N > cont_step_count:
        # N >= minimum contiguous path
        steps = []
        for n in range(cont_step_count):
            step = delta.map(sgn)
            steps.append(step)
            delta = delta.map(lambda x: x - sgn(x))

        ret = distribute(list(itertools.accumulate([rgb_a] + steps)), N)

    else:
        # N is shorter than minimum contiguous path
        ret = zip(
                distribute(interval(rgb_a[0], rgb_b[0]), N),
                distribute(interval(rgb_a[1], rgb_b[1]), N),
                distribute(interval(rgb_a[2], rgb_b[2]), N),
                )

    return tuple(rgb6_to_color(i) for i in ret)


def gradient_rgb(A, B, N):
    # Calculate gradient in RGB
    # a = (A.r, A.g, A.b)
    # b = (B.r, B.g, B.b)
    #
    # ret = [A]
    # for t in (i / (N - 1) for i in range(1, N - 1)):
    #     ret.append(ColorRGB(tuple(map(int, lerp(a, b, t)))))
    # ret.append(B)
    # return tuple(ret)

    if N is None:
        N = 7

    # Calculate gradient in HSV
    import colorsys
    a = vector(colorsys.rgb_to_hsv(A.r / 255, A.g / 255, A.b / 255))
    b = vector(colorsys.rgb_to_hsv(B.r / 255, B.g / 255, B.b / 255))

    # Choose shorter hue gradient path
    if abs(b[0] - a[0]) > 0.5:
        if b[0] < a[0]:
            b[0] += 1
        else:
            a[0] += 1

    ret = [A]
    for t in (i / (N - 1) for i in range(1, N - 1)):
        c = lerp(a, b, t)
        ret.append(ColorRGB(vector(colorsys.hsv_to_rgb(*c)).map(lambda x: int(x * 255))))

    ret.append(B)

    return tuple(ret)
