from .test_utils import *

from smol.paints import *


class TestPaint(TestCase):
    def test_nocolor(self):
        self.eq(paint(), nocolor)
        self.eq(nocolor(), '')
        self.eq(nocolor('text'), 'text')
        self.eq(nocolor.seq, '')
        self.eq('{}'.format(nocolor), '\033[m')

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

    def test_bg(self):
        self.eq(1 / red,      paint(bg=1))
        self.eq(1 / green,    paint(bg=2))
        self.eq(1 / yellow,   paint(bg=3))
        self.eq(1 / blue,     paint(bg=4))
        self.eq(1 / magenta,  paint(bg=5))
        self.eq(1 / cyan,     paint(bg=6))
        self.eq(1 / white,    paint(bg=7))
        self.eq(1 / orange,   paint(bg=208))

    def test_call(self):
        self.eq(black('color'),   '\033[38;5;0mcolor\033[m')
        self.eq(red('color'),     '\033[38;5;1mcolor\033[m')
        self.eq(green('color'),   '\033[38;5;2mcolor\033[m')
        self.eq(yellow('color'),  '\033[38;5;3mcolor\033[m')
        self.eq(blue('color'),    '\033[38;5;4mcolor\033[m')
        self.eq(magenta('color'), '\033[38;5;5mcolor\033[m')
        self.eq(cyan('color'),    '\033[38;5;6mcolor\033[m')
        self.eq(white('color'),   '\033[38;5;7mcolor\033[m')
        self.eq(orange('color'),  '\033[38;5;208mcolor\033[m')

    def test_or(self):
        self.eq(black | (1 / yellow), paint(fg=0, bg=3))

    def test_div(self):
        ry = red / yellow
        self.eq(ry, paint(fg=1, bg=3))
        self.eq(ry.seq, '\033[38;5;1;48;5;3m')

    def test_rgb(self):
        self.eq(paint(160, 90, 0)('test'), '\033[38;2;160;90;0mtest\033[m')

    def test_decolor(self):
        self.eq(decolor(orange('test')), 'test')
        self.eq(decolor('\033[1;31mred\033[m'), 'red')
