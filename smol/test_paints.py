from .test_utils import *

from smol.paints import *


class TestDye(TestCase):
    def test_dye_facade(self):
        # arg unpack
        self.eq(dye((208,)), dye(208))

        # copy_ctor
        self.eq(dye(dye(208)), dye(208))

        # dye256
        self.is_true(issubclass(dye256, dye))
        orange = dye(208)
        self.is_true(isinstance(orange, dye256))
        self.is_true(isinstance(orange, dye))

        # dyergb
        self.is_true(issubclass(dyergb, dye))
        orange = dye('#A05A00')
        self.is_true(isinstance(orange, dyergb))
        self.is_true(isinstance(orange, dye))

    def test_dye_invalid(self):
        with self.assertRaises(TypeError):
            dye(True)

        with self.assertRaises(TypeError):
            dye256(True)

        with self.assertRaises(TypeError):
            dyergb(True)

    def test_dye256(self):
        orange = dye(208)
        self.eq(orange('prefix'), 'prefix;5;208')
        self.eq(int(orange), 208)
        repr(orange)

    def test_dyergb(self):
        orange = dyergb((160, 90, 0))
        self.eq(dyergb(orange), orange)
        self.eq(orange, dyergb('#A05A00'))
        self.eq(orange.r, 160)
        self.eq(orange.g, 90)
        self.eq(orange.b, 0)
        self.eq(int(orange), 0xa05a00)
        self.eq(str(orange), '#A05A00')

        with self.assertRaises(TypeError):
            dyergb(True)

        repr(orange)

        self.eq(orange('prefix'), 'prefix;2;160;90;0')


class TestPaint(TestCase):
    def test_nocolor(self):
        self.eq(paint(), nocolor)
        self.eq(nocolor(), '')
        self.eq(nocolor('text'), 'text')
        self.eq(nocolor.seq, '')
        self.eq(str(nocolor), '\033[m')
        self.eq('{}'.format(nocolor), '\033[m')
        self.is_true(repr(paint()).startswith('paint'))

    def test_fg(self):
        self.eq(black.seq,    '\033[38;5;0m')
        self.eq(red.seq,      '\033[38;5;1m')
        self.eq(green.seq,    '\033[38;5;2m')
        self.eq(yellow.seq,   '\033[38;5;3m')
        self.eq(blue.seq,     '\033[38;5;4m')
        self.eq(magenta.seq,  '\033[38;5;5m')
        self.eq(cyan.seq,     '\033[38;5;6m')
        self.eq(white.seq,    '\033[38;5;7m')
        self.eq(orange.seq,   '\033[38;5;208m')

    def test_str(self):
        self.eq(str(black),         '\033[38;5;0m')
        self.eq(str(red.seq),       '\033[38;5;1m')
        self.eq(str(green.seq),     '\033[38;5;2m')
        self.eq(str(yellow.seq),    '\033[38;5;3m')
        self.eq(str(blue.seq),      '\033[38;5;4m')
        self.eq(str(magenta.seq),   '\033[38;5;5m')
        self.eq(str(cyan.seq),      '\033[38;5;6m')
        self.eq(str(white.seq),     '\033[38;5;7m')
        self.eq(str(orange.seq),    '\033[38;5;208m')

    def test_bg(self):
        self.eq(~red,      paint(bg=1))
        self.eq(~green,    paint(bg=2))
        self.eq(~yellow,   paint(bg=3))
        self.eq(~blue,     paint(bg=4))
        self.eq(~magenta,  paint(bg=5))
        self.eq(~cyan,     paint(bg=6))
        self.eq(~white,    paint(bg=7))
        self.eq(~orange,   paint(bg=208))

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

    def test_add(self):
        self.eq((red + yellow) + white, white)

    def test_or(self):
        self.eq(black | (~yellow), paint(fg=0, bg=3))

    def test_div(self):
        ry = red / yellow
        self.eq(ry, paint(fg=1, bg=3))
        self.eq(ry.seq, '\033[38;5;1;48;5;3m')

    def test_invert(self):
        self.eq((~yellow), paint(bg=3))

    def test_rgb(self):
        self.eq(paint(fg=(160, 90, 0))('test'), '\033[38;2;160;90;0mtest\033[m')
        self.eq(paint(bg=(160, 90, 0))('test'), '\033[48;2;160;90;0mtest\033[m')

    def test_decolor(self):
        self.eq(decolor(orange('test')), 'test')
        self.eq(decolor('\033[1;31mred\033[m'), 'red')
