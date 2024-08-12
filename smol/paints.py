import re
import abc
import itertools

from .math import sgn
from .math import vector
from .math import lerp
from .math import interval


# try:
#     from icecream import ic
# except ImportError:  # Graceful fallback if IceCream isn't installed.
#     ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


__all__ = ['paint']
__all__ += ['nocolor', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'orange']
__all__ += ['decolor']
__all__ += ['dye', 'dye256', 'dyergb', 'gradient']


def is_uint8(i):
    return isinstance(i, int) and not isinstance(i, bool) and 0 <= i < 256


class DyeTrait(abc.ABC):
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
        return paint(bg=self)

    def __truediv__(self, other):
        if not isinstance(other, dye):
            raise TypeError('Only dye() / dye() is allowed')
        return paint(fg=self, bg=other)

    def __or__(self, other):
        if isinstance(other, dye):
            return self if self.seq else other
        return paint(fg=self) | other


class dye(abc.ABC):
    def __new__(cls, *args, **kwargs):
        # unpack
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            args = args[0]

        # empty
        if not args:
            return dye256(None)

        # copy ctor
        elif len(args) == 1 and issubclass(type(args[0]), dye):
            return type(args[0])(*args, **kwargs)

        # dye256 ctor
        elif len(args) == 1 and (args[0] is None or is_uint8(args[0])):
            return dye256(*args, **kwargs)

        # dyergb ctor
        elif len(args) == 3 and all(is_uint8(i) for i in args):
            return dyergb(*args, **kwargs)

        # dyergb ctor #xxxxxx
        elif len(args) == 1 and isinstance(args[0], str) and re.match(r'^#[0-9a-f]{6}$', args[0].lower()):
            return dyergb(*args, **kwargs)

        raise TypeError('Invalid arguments')


class dye256(DyeTrait):
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

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.code)

    def __int__(self):
        return self.code

dye.register(dye256)


class dyergb(DyeTrait):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            args = args[0]

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
        return 'dyergb({}, {}, {})'.format(self.r, self.g, self.b)

    def __int__(self):
        return (self.r << 16) | (self.g << 8) | (self.b)

dye.register(dyergb)


class paint:
    def __init__(self, fg=None, bg=None):
        self.fg = dye(fg)
        self.bg = dye(bg)

        seq = ';'.join(filter(None, [
            '38;' + self.fg.seq if self.fg.seq else None,
            '48;' + self.bg.seq if self.bg.seq else None,
            ]))
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

    def __truediv__(self, other):
        return paint(fg=self.fg, bg=other.fg)

    def __invert__(self):
        return paint(fg=self.bg, bg=self.fg)

    def __eq__(self, other):
        return self.seq == other.seq


nocolor = dye()
black = dye(0)
red = dye(1)
green = dye(2)
yellow = dye(3)
blue = dye(4)
magenta = dye(5)
cyan = dye(6)
white = dye(7)
orange = dye(208)


decolor_regex = re.compile('\033' + r'\[[\d;]*m')
def decolor(s):
    return decolor_regex.sub('', s)


def gradient(A, B, N=None):
    if not isinstance(A, dye) or not isinstance(B, dye):
        raise TypeError('Can only calculate gradient() on dye objects')

    if N is not None and not isinstance(N, int):
        raise TypeError('N must be a integer')

    if N is not None and N < 2:
        raise ValueError('N={} is too small'.format(N))

    if N == 2:
        return (A, B)

    if isinstance(A, dye256) and isinstance(B, dye256):
        return gradient_color256(A, B, N=N)

    if isinstance(A, dyergb) and isinstance(B, dyergb):
        return gradient_rgb(A, B, N=N)

    return (A, B)


def gradient_color256(A, B, N=None):
    if A.code in range(232, 256) and B.code in range(232, 256):
        return gradient_color256_gray(A, B, N)

    if A.code in range(16, 232) and B.code in range(16, 232):
        return gradient_color256_rgb(A, B, N)

    return (A, B)


def distribute(samples, N):
    if N is None:
        return samples

    n = len(samples)

    if N == n:
        return samples

    if N < n:
        # Averaging skipped samples to into N-1 gaps
        skip_count = n - N
        gap_count = N - 1

        probe = 0
        dup, rem = divmod(skip_count, gap_count)

        ret = [samples[0]]
        for i in range(gap_count):
            probe += 1 + dup + (i < rem)
            ret.append(samples[probe])

    if N > n:
        # Duplicate samples to match N
        ret = []
        dup, rem = divmod(N, n)
        for i in range(n):
            for d in range(dup + (i < rem)):
                ret.append(samples[i])

    return ret


def gradient_color256_gray(A, B, N=None):
    a, b = A.code, B.code
    direction = sgn(b - a)
    n = abs(b - a) + 1
    return tuple(dye256(c) for c in distribute(interval(a, b), N or n))


def gradient_color256_rgb(A, B, N=None):
    def color_to_rgb6(p):
        c = int(p) - 16
        r = c // 36
        g = (c % 36) // 6
        b = c % 6
        return vector(r, g, b)

    def rgb6_to_color(rgb6):
        return dye256(rgb6[0] * 36 + rgb6[1] * 6 + rgb6[2] + 16)

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

        ret = distribute(list(itertools.accumulate(steps, initial=rgb_a)), N)

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
    #     ret.append(dyergb(tuple(map(int, lerp(a, b, t)))))
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

    ret = [A]
    for t in (i / (N - 1) for i in range(1, N - 1)):
        c = lerp(a, b, t)
        ret.append(dyergb(vector(colorsys.hsv_to_rgb(*c)).map(lambda x: int(x * 255))))

    ret.append(B)

    return tuple(ret)
