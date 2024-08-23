from .test_utils import *

from smol import *


class TestDyeFacade(TestCase):
    def test_dye_facade(self):
        # arg unpack
        self.eq(dye((208,)), dye(208))
        self.eq(dye([208]), dye(208))
        self.eq(dye((0xC0, 0xFF, 0xEE,)), dye('#C0FFEE'))
        self.eq(dye([0xC0, 0xFF, 0xEE]), dye('#C0FFEE'))

        # copy_ctor
        self.eq(dye(dye(208)), dye(208))

        # subclass
        self.is_true(issubclass(dye256, dye))
        self.is_true(issubclass(dyergb, dye))

        # dye256
        orange = dye(208)
        self.is_true(isinstance(orange, dye256))
        self.is_true(isinstance(orange, dye))

        # dyergb
        coffee = dye((0xC0, 0xFF, 0xEE))
        self.is_true(isinstance(coffee, dyergb))
        self.is_true(isinstance(coffee, dye))

        # dyergb
        coffee = dye('#C0FFEE')
        self.is_true(isinstance(coffee, dyergb))
        self.is_true(isinstance(coffee, dye))

    def test_dye_invalid_value(self):
        with self.assertRaises(TypeError):
            dye(True)

        with self.assertRaises(TypeError):
            dye256(True)

        with self.assertRaises(TypeError):
            dyergb(True)


class TestDyeTrait(TestCase):
    def setUp(self):
        self.orange = dye(208)
        self.coffee = dye('#C0FFEE')

    def test_repr(self):
        self.is_true(repr(self.orange).startswith('dye'))
        self.is_true(repr(self.coffee).startswith('dye'))

    def test_int(self):
        self.eq(int(self.orange), 208)
        self.eq(int(self.coffee), 0xC0FFEE)

    def test_fg(self):
        self.eq(self.orange('text'), '\033[38;5;208mtext\033[m')
        self.eq(self.coffee('text'), '\033[38;2;192;255;238mtext\033[m')
        self.eq(self.orange.fg('text'), '\033[38;5;208mtext\033[m')
        self.eq(self.coffee.fg('text'), '\033[38;2;192;255;238mtext\033[m')

    def test_bg(self):
        self.eq(self.orange.bg('text'), '\033[48;5;208mtext\033[m')
        self.eq(self.coffee.bg('text'), '\033[48;2;192;255;238mtext\033[m')

    def test_str(self):
        self.eq(str(self.orange), '\033[38;5;208m')
        self.eq(str(self.coffee), '\033[38;2;192;255;238m')

    def test_invert(self):
        self.eq(str(~self.orange), '\033[48;5;208m')
        self.eq(str(~self.coffee), '\033[48;2;192;255;238m')
        self.is_true(isinstance(~self.orange, paint))
        self.is_true(isinstance(~self.coffee, paint))

    def test_div(self):
        self.eq(self.orange / self.coffee, paint(fg=self.orange, bg=self.coffee))

        with self.assertRaises(TypeError):
            self.orange / 1

    def test_or(self):
        self.eq(nocolor | self.coffee, self.coffee)
        self.eq(self.orange | self.coffee, self.orange)


class TestDye256(TestCase):
    def test_dye256(self):
        orange = dye(208)
        self.eq(orange.code, 208)


class TestDyeRGB(TestCase):
    def test_dyergb_empty(self):
        self.eq(dyergb().seq, '')

    def test_dyergb(self):
        orange = dyergb([160, 90, 0])
        self.eq(orange.r, 160)
        self.eq(orange.g, 90)
        self.eq(orange.b, 0)
        self.eq(int(orange), 0xA05A00)


class TestBuiltInDyes(TestCase):
    def test_nocolor(self):
        self.eq(nocolor(), '')
        self.eq(nocolor('text'), 'text')
        self.eq(str(nocolor), '\033[m')
        self.eq('{}'.format(nocolor), '\033[m')

    def test_str(self):
        self.eq(str(black),     '\033[38;5;0m')
        self.eq(str(red),       '\033[38;5;1m')
        self.eq(str(green),     '\033[38;5;2m')
        self.eq(str(yellow),    '\033[38;5;3m')
        self.eq(str(blue),      '\033[38;5;4m')
        self.eq(str(magenta),   '\033[38;5;5m')
        self.eq(str(cyan),      '\033[38;5;6m')
        self.eq(str(white),     '\033[38;5;7m')
        self.eq(str(orange),    '\033[38;5;208m')

    def test_invert(self):
        self.eq(~red,      paint(bg=red))
        self.eq(~green,    paint(bg=green))
        self.eq(~yellow,   paint(bg=yellow))
        self.eq(~blue,     paint(bg=blue))
        self.eq(~magenta,  paint(bg=magenta))
        self.eq(~cyan,     paint(bg=cyan))
        self.eq(~white,    paint(bg=white))
        self.eq(~orange,   paint(bg=orange))

    def test_call(self):
        self.eq(black('text'),   '\033[38;5;0mtext\033[m')
        self.eq(red('text'),     '\033[38;5;1mtext\033[m')
        self.eq(green('text'),   '\033[38;5;2mtext\033[m')
        self.eq(yellow('text'),  '\033[38;5;3mtext\033[m')
        self.eq(blue('text'),    '\033[38;5;4mtext\033[m')
        self.eq(magenta('text'), '\033[38;5;5mtext\033[m')
        self.eq(cyan('text'),    '\033[38;5;6mtext\033[m')
        self.eq(white('text'),   '\033[38;5;7mtext\033[m')
        self.eq(orange('text'),  '\033[38;5;208mtext\033[m')


class TestPaint(TestCase):
    def test_repr(self):
        self.is_true(repr(paint()).startswith('paint'))

    def test_or(self):
        self.eq(black | (~yellow), paint(fg=0, bg=3))

    def test_div(self):
        ry = red / yellow
        bg = blue / green
        rybg = ry / bg
        self.eq(rybg, paint(fg=red, bg=blue))
        self.eq(rybg('text'), '\033[38;5;1;48;5;4mtext\033[m')

    def test_invert(self):
        ry = red / yellow
        bg = blue / green
        rybg = ry / bg
        self.eq(~rybg, paint(fg=blue, bg=red))
        self.eq((~rybg)('text'), '\033[38;5;4;48;5;1mtext\033[m')


class TestDecolor(TestCase):
    def test_decolor(self):
        self.eq(decolor(orange('test')), 'test')
        self.eq(decolor('\033[1;31mred\033[m'), 'red')


class TestGradient(TestCase):
    def test_invalid_values(self):
        with self.assertRaises(TypeError):
            gradient(True, False)

        A = dye()
        B = dye()

        with self.assertRaises(TypeError):
            gradient(A, B, 1.5)

        with self.assertRaises(ValueError):
            gradient(A, B, 1)

    def test_trivial(self):
        # N=2 trivial case
        A = dye(39)
        B = dye(214)
        self.eq(gradient(A, B, 2), (A, B))

        # dye256() and dyergb() case
        A = dye(39)
        B = dye('#C0FFEE')
        self.eq(gradient(A, B), (A, B))

        # dye256() rgb6 and gray case
        A = dye(39)
        B = dye(255)
        self.eq(gradient(A, B), (A, B))

    def test_dye256_gray(self):
        A = dye(235)
        B = dye(245)

        # default length
        res = gradient(A, B)
        ans = tuple(range(235, 246))
        self.eq(res, tuple(map(dye, ans)))

        # shorter length
        res = gradient(A, B, N=5)
        ans = (235, 238, 241, 243, 245)
        self.eq(res, tuple(map(dye, ans)))

        # longer length
        res = gradient(A, B, N=15)
        ans = (235, 235, 236, 236, 237, 237, 238, 238, 239, 240, 241, 242, 243, 244, 245)
        self.eq(res, tuple(map(dye, ans)))


    def test_dye256_rgb(self):
        A = dye(39)
        B = dye(214)

        # default length
        res = gradient(A, B)
        ans = (39 ,74 ,109 ,144 ,179 ,214)
        self.eq(res, tuple(map(dye, ans)))

        # shorter length
        res = gradient(A, B, N=4)
        ans = (39, 109, 179, 214)
        self.eq(res, tuple(map(dye, ans)))

        # longer length
        res = gradient(A, B, N=15)
        ans = (39, 39, 39, 74, 74, 74, 109, 109, 109, 144, 144, 179, 179, 214, 214)
        self.eq(res, tuple(map(dye, ans)))

    def test_dyergb(self):
        A = dye(242, 5, 148)
        B = dye(146, 219, 189)

        # default length
        res = gradient(A, B)
        ans = (dye(242, 5, 148),
               dye(223, 30, 238),
               dye(137, 55, 234),
               dye(79, 80, 230),
               dye(102, 161, 226),
               dye(124, 217, 222),
               dye(146, 219, 189))

        self.eq(res, ans)

        # shorter length
        res = gradient(A, B, N=4)
        ans = (dye(242, 5, 148),
               dye(137, 55, 234),
               dye(102, 161, 226),
               dye(146, 219, 189))
        self.eq(res, tuple(map(dye, ans)))

        # longer length
        res = gradient(A, B, N=15)
        ans = (dyergb(242, 5, 148),
               dyergb(240, 16, 196),
               dyergb(237, 26, 238),
               dyergb(196, 37, 237),
               dyergb(159, 48, 235),
               dyergb(127, 58, 233),
               dyergb(100, 69, 232),
               dyergb(79, 80, 230),
               dyergb(89, 118, 228),
               dyergb(99, 151, 227),
               dyergb(108, 179, 225),
               dyergb(118, 203, 223),
               dyergb(127, 222, 221),
               dyergb(136, 220, 203),
               dyergb(146, 219, 189),)
        self.eq(res, ans)

        A = dye('#FF1100')
        B = dye('#FF0011')
        res = gradient(A, B, N=3)
        self.eq(res, (A, dye('#FF0000'), B))

        A = dye('#FF0011')
        B = dye('#FF1100')
        res = gradient(A, B, N=3)
        self.eq(res, (A, dye('#FF0000'), B))
