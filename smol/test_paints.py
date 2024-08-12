from .test_utils import *

from smol.paints import *


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
