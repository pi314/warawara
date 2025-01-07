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
        return isinstance(other, self.__class__) and self.seq == other.seq

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

    # Copy ctor
    elif len(args) == 1 and issubclass(type(args[0]), Color):
        return type(args[0])(*args, **kwargs)

    # Color256 ctor
    elif len(args) == 1 and (args[0] is None or is_uint8(args[0])):
        return Color256(*args, **kwargs)

    # ColorRGB ctor
    elif len(args) == 3 and all(is_uint8(i) for i in args):
        return ColorRGB(*args, **kwargs)

    # ColorRGB ctor #RRGGBB
    elif len(args) == 1 and isinstance(args[0], str) and re.fullmatch(r'#[0-9A-Fa-f]{6}', args[0]):
        return ColorRGB(*args, **kwargs)

    # ColorHSV @H,S,V format
    elif len(args) == 1 and isinstance(args[0], str) and re.fullmatch(r'@[0-9]+,[0-9]+,[0-9]+', args[0]):
        return ColorHSV(*args, **kwargs)

    raise TypeError('Invalid arguments: ' + ' '.join(args))


@export
class Color256(Color):
    def __init__(self, index=None):
        if isinstance(index, self.__class__):
            index = index.index

        self.index = index

        if index is None:
            self.seq = ''
        elif is_uint8(index):
            self.seq = '5;{}'.format(self.index)
        else:
            raise TypeError('Invalid color index: {}'.format(index))

    @property
    def code(self):
        return self.index

    def to_rgb(self):
        if self.index < 16:
            base = 0xFF if (self.index > 7) else 0x80
            is_7 = (self.index == 7)
            is_8 = (self.index == 8)
            R = base * ((self.index & 0x1) != 0) + (0x40 * is_7) + (0x80 * is_8)
            G = base * ((self.index & 0x2) != 0) + (0x40 * is_7) + (0x80 * is_8)
            B = base * ((self.index & 0x4) != 0) + (0x40 * is_7) + (0x80 * is_8)

        elif self.index < 232:
            base = self.index - 16
            index_R = (base // 36)
            index_G = ((base % 36) // 6)
            index_B = (base % 6)
            R = (55 + index_R * 40) if index_R > 0 else 0
            G = (55 + index_G * 40) if index_G > 0 else 0
            B = (55 + index_B * 40) if index_B > 0 else 0

        else:
            R = G = B = (self.index - 232) * 10 + 8

        return ColorRGB(R, G, B)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.index)

    def __int__(self):
        return self.index


@export
class ColorRGB(Color):
    def __init__(self, *args, overflow=False):
        args = unwrap_one(args)

        type_check = (lambda x: 0 <= x < 256
                      if not overflow
                      else lambda x: isinstance(x, (int, float)))

        self.r = None
        self.g = None
        self.b = None

        if not args:
            return

        # Copy ctor
        elif len(args) == 1 and isinstance(args[0], self.__class__):
            other = args[0]
            (self.r, self.g, self.b) = (other.r, other.g, other.b)

        # #RRGGBB format
        elif len(args) == 1 and isinstance(args[0], str) and re.fullmatch(r'#[0-9A-Fa-f]{6}', args[0]):
            rgb_str = args[0][1:]
            self.r = int(rgb_str[0:2], 16)
            self.g = int(rgb_str[2:4], 16)
            self.b = int(rgb_str[4:6], 16)

        # (num, num, num) format
        elif len(args) == 3 and all(type_check(i) for i in args):
            (self.r, self.g, self.b) = args

        else:
            raise TypeError('Invalid RGB value: {}'.format(args))

    def __repr__(self):
        return 'ColorRGB({}, {}, {})'.format(self.r, self.g, self.b)

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def seq(self):
        if None in self.rgb:
            return ''

        return '2;{};{};{}'.format(
                min(int(self.r), 255),
                min(int(self.g), 255),
                min(int(self.b), 255))

    def __add__(self, other):
        rgb = vector(self.rgb) + vector(other.rgb)
        return ColorRGB(*rgb, overflow=True)

    def __mul__(self, num):
        return ColorRGB(vector(self.rgb) * num, overflow=True)

    def __floordiv__(self, num):
        return ColorRGB(vector(self.rgb) // num, overflow=True)

    def __int__(self):
        return (min(int(self.r), 255) << 16) | (min(int(self.g), 255) << 8) | (min(int(self.b), 255))

    def __format__(self, spec):
        if not spec:
            return str(self)

        if spec in ('#x', '#X'):
            r = min(int(self.r), 255)
            g = min(int(self.g), 255)
            b = min(int(self.b), 255)
            x = spec[1]
            return '#{r:0>2{x}}{g:0>2{x}}{b:0>2{x}}'.format(r=r, g=g, b=b, x=x)

        return format(self.rgb, spec)

    def to_hsv(self, overflow=False):
        import colorsys
        hsv = colorsys.rgb_to_hsv(self.r / 255, self.g / 255, self.b / 255)
        return ColorHSV(hsv[0] * 359, hsv[1] * 100, hsv[2] * 100, overflow=overflow)


@export
class ColorHSV(Color):
    def __init__(self, *args, overflow=False):
        args = unwrap_one(args)

        self.h = None
        self.s = None
        self.v = None

        h = None
        s = None
        v = None

        if not args:
            return

        # Copy ctor
        elif len(args) == 1 and isinstance(args[0], self.__class__):
            other = args[0]
            (h, s, v) = (other.h, other.s, other.v)

        # @H,S,V format
        elif len(args) == 1 and isinstance(args[0], str) and re.fullmatch(r'@[0-9]+,[0-9]+,[0-9]+', args[0]):
            (h, s, v) = list(map(lambda x: int(x, 10), args[0][1:].split(',')))

        # (num, num, num) format
        elif len(args) == 3:
            (h, s, v) = args

        if (all(isinstance(x, (int, float)) for x in (h, s, v)) and
            overflow or
            ((0 <= s <= 100) and
             (0 <= v <= 100))):
            (self.h, self.s, self.v) = (h % 360, s, v)
            self._rgb = self.to_rgb(overflow)

        else:
            raise TypeError('Invalid HSV value: {}'.format(args))

    def __repr__(self):
        return 'ColorHSV({:}deg, {:}%, {:}%)'.format(int(self.h), int(self.s), int(self.v))

    @property
    def hsv(self):
        return (self.h, self.s, self.v)

    @property
    def seq(self):
        if None in self.hsv:
            return ''
        return self._rgb.seq

    def __add__(self, other):
        hsv = vector(self.hsv) + vector(other.hsv)
        return ColorHSV(*hsv, overflow=True)

    def __mul__(self, num):
        return ColorHSV(vector(self.hsv) * num, overflow=True)

    def __floordiv__(self, num):
        return ColorHSV(vector(self.hsv) // num, overflow=True)

    def __int__(self):
        return (min(int(self.h), 359) * 1000000) + (min(int(self.s), 100) * 1000) + (min(int(self.v), 100))

    def __format__(self, spec):
        if not spec:
            return str(self)
        if spec == '#':
            return '(@{}, {}%, {}%)'.format(int(self.h), int(self.s), int(self.v))
        return format(self.hsv, spec)

    def to_rgb(self, overflow=False):
        import colorsys
        return ColorRGB(vector(colorsys.hsv_to_rgb(
            min(self.h, 359) / 360,
            min(self.s, 100) / 100,
            min(self.v, 100) / 100)) * 255, overflow=overflow)


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

@export
def paint(fg=None, bg=None):
    return ColorCompound(fg=fg, bg=bg)


export('nocolor')
nocolor = color()

named_colors = [
        (0, ('black',)),
        (1, ('maroon',)),
        (2, ('green',)),
        (3, ('olive',)),
        (4, ('navy',)),
        (5, ('purple',)),
        (6, ('teal',)),
        (7, ('silver',)),
        (8, ('gray', 'grey',)),
        (9, ('red',)),
        (10, ('lime',)),
        (11, ('yellow',)),
        (12, ('blue',)),
        (13, ('fuchsia', 'magenta',)),
        (14, ('aqua', 'cyan',)),
        (15, ('aliceblue', 'azure', 'floralwhite', 'ghostwhite', 'ivory',
              'lavenderblush', 'mintcream', 'snow', 'white',)),
        (17, ('midnightblue',)),
        (18, ('darkblue',)),
        (20, ('mediumblue',)),
        (22, ('darkgreen',)),
        (28, ('forestgreen',)),
        (29, ('seagreen',)),
        (30, ('darkcyan',)),
        (33, ('dodgerblue',)),
        (37, ('lightseagreen',)),
        (39, ('deepskyblue',)),
        (44, ('darkturquoise',)),
        (48, ('mediumspringgreen', 'springgreen',)),
        (54, ('indigo',)),
        (60, ('darkslateblue',)),
        (62, ('royalblue', 'slateblue',)),
        (64, ('olivedrab',)),
        (66, ('slategray', 'slategrey',)),
        (67, ('steelblue',)),
        (69, ('cornflowerblue',)),
        (71, ('mediumseagreen',)),
        (73, ('cadetblue',)),
        (77, ('limegreen',)),
        (79, ('mediumaquamarine',)),
        (80, ('mediumturquoise', 'turquoise',)),
        (88, ('darkred',)),
        (90, ('darkmagenta',)),
        (92, ('blueviolet', 'darkviolet',)),
        (94, ('saddlebrown',)),
        (98, ('darkorchid', 'mediumpurple',)),
        (99, ('mediumslateblue',)),
        (102, ('lightslategray', 'lightslategrey',)),
        (108, ('darkseagreen',)),
        (113, ('yellowgreen',)),
        (117, ('lightskyblue', 'skyblue',)),
        (118, ('chartreuse', 'lawngreen',)),
        (120, ('lightgreen', 'palegreen',)),
        (122, ('aquamarine',)),
        (124, ('brown', 'firebrick',)),
        (130, ('sienna',)),
        (134, ('mediumorchid',)),
        (135, ('murasaki',)),
        (136, ('darkgoldenrod',)),
        (138, ('rosybrown',)),
        (143, ('darkkhaki',)),
        (152, ('lightblue', 'lightsteelblue', 'powderblue',)),
        (154, ('greenyellow',)),
        (159, ('paleturquoise',)),
        (161, ('crimson',)),
        (162, ('mediumvioletred',)),
        (166, ('chocolate', 'clementine',)),
        (167, ('indianred',)),
        (168, ('palevioletred',)),
        (170, ('orchid',)),
        (173, ('peru',)),
        (174, ('darksalmon',)),
        (178, ('goldenrod',)),
        (180, ('burlywood', 'tan',)),
        (182, ('plum', 'thistle',)),
        (195, ('lightcyan',)),
        (198, ('deeppink',)),
        (202, ('orangered',)),
        (203, ('tomato',)),
        (205, ('hotpink',)),
        (208, ('darkorange',)),
        (209, ('coral', 'salmon',)),
        (210, ('lightcoral',)),
        (213, ('violet',)),
        (214, ('orange',)),
        (215, ('sandybrown',)),
        (216, ('lightsalmon',)),
        (217, ('lightpink',)),
        (218, ('pink',)),
        (220, ('gold',)),
        (222, ('khaki',)),
        (223, ('moccasin', 'navajowhite', 'palegoldenrod',
               'peachpuff', 'wheat',)),
        (224, ('bisque', 'mistyrose',)),
        (230, ('antiquewhite', 'beige', 'blanchedalmond',
               'cornsilk', 'lemonchiffon',
               'lightgoldenrodyellow', 'lightyellow',
               'oldlace', 'papayawhip',)),
        (238, ('darkslategray', 'darkslategrey',)),
        (239, ('darkolivegreen',)),
        (242, ('dimgray', 'dimgrey',)),
        (248, ('darkgray', 'darkgrey',)),
        (252, ('lightgray', 'lightgrey',)),
        (253, ('gainsboro',)),
        (255, ('honeydew', 'lavender', 'linen', 'seashell', 'whitesmoke',)),
]
export('names')
names = tuple(name for index, names in named_colors for name in names)
def _setup_named_colors():
    for index, names in named_colors:
        clr = color(index)
        for name in names:
            globals()[name] = clr
            export(name)
_setup_named_colors()
del _setup_named_colors


decolor_regex = re.compile('\033' + r'\[[\d;]*m')

@export
def decolor(s):
    return decolor_regex.sub('', s)


@export
def gradient(A, B, N=None, reverse=False, clockwise=None):
    if not isinstance(A, Color) or not isinstance(B, Color):
        raise TypeError('Can only calculate gradient() on Color objects')

    if N is not None and not isinstance(N, int):
        raise TypeError('N must be a integer')

    if N is not None and N < 2:
        raise ValueError('N={} is too small'.format(N))

    ret = None
    if N == 2:
        ret = (A, B)

    elif isinstance(A, Color256) and isinstance(B, Color256):
        ret = gradient_color256(A, B, N=N)

    elif isinstance(A, ColorRGB) and isinstance(B, ColorRGB):
        ret = gradient_rgb(A, B, N=N)

    elif isinstance(A, ColorHSV) and isinstance(B, ColorHSV):
        ret = gradient_hsv(A, B, N=N, clockwise=clockwise)

    else:
        ret = (A, B)

    if reverse:
        return ret[::-1]
    else:
        return ret


def gradient_color256(A, B, N=None):
    if A.index in range(232, 256) and B.index in range(232, 256):
        return gradient_color256_grayscale_range(A, B, N)

    if A.index in range(16, 232) and B.index in range(16, 232):
        return gradient_color256_rgb_range(A, B, N)

    return (A, B)


def gradient_color256_grayscale_range(A, B, N=None):
    a, b = A.index, B.index
    direction = sgn(b - a)
    n = abs(b - a) + 1
    return tuple(Color256(c) for c in distribute(interval(a, b), N or n))


def gradient_color256_rgb_range(A, B, N=None):
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

    if N is None:
        import math
        dist_hue = math.ceil(abs(a[0] - b[0]) * 12)
        dist_sat = math.floor(abs(a[1] - b[1]) * 6)
        dist_val = math.floor(abs(a[2] - b[2]) * 6)
        N = max(dist_hue, dist_sat, dist_val)

    ret = [A]
    for t in (i / (N - 1) for i in range(1, N - 1)):
        c = lerp(a, b, t)
        ret.append(ColorRGB(vector(colorsys.hsv_to_rgb(*c)).map(lambda x: int(x * 255))))

    ret.append(B)

    return tuple(ret)


def gradient_hsv(A, B, N, clockwise):
    # Calculate gradient in HSV
    a = vector(A.hsv)
    b = vector(B.hsv)

    if clockwise == True:
        b[0] += 360 if (a[0] > b[0]) else 0
    elif clockwise == False:
        a[0] += 360 if (a[0] < b[0]) else 0

    if N is None:
        import math
        dist_hue = math.ceil(abs(a[0] - b[0]) / 30)
        dist_sat = math.floor(abs(a[1] - b[1]) / 10)
        dist_val = math.floor(abs(a[2] - b[2]) / 10)
        N = max(dist_hue, dist_sat, dist_val)

    ret = [A]
    for t in (i / (N - 1) for i in range(1, N - 1)):
        c = lerp(a, b, t)
        ret.append(ColorHSV(*c))

    ret.append(B)

    return tuple(ret)
