#!/usr/bin/env python3

import sys
import argparse

from .lib_tui import strwidth, ljust, retab


class BoxChar:
    def __init__(self, ch):
        self.ch = ch

    def __str__(self):
        return self.ch

    def __call__(self, width):
        return self.ch * width

    def __add__(self, rhs):
        return self.ch + rhs

    def __radd__(self, lhs):
        return lhs + self.ch

    def __mul__(self, count):
        return self.ch * count

    def __rmul__(self, count):
        return count * self.ch

    def __eq__(self, other):
        return other == self.ch


def BoxConfig(seq):
    '''
       0  1  2
        ╭───╮
      3 │ ┬4│ 5
        ╰───╯
       6  7  8

          ╯ 9
    '''
    if len(seq) == 1:
        if seq in '╭─╮│╰─╯┬':
            return [BoxChar(c) for c in '╭─╮│┬│╰─╯╯']
        elif seq in '┌─┐│└─┘┬':
            return [BoxChar(c) for c in '┌─┐│┬│└─┘╯']
        elif seq in '┏━┓┃┗━┛┳':
            return [BoxChar(c) for c in '┏━┓┃┳┃┗━┛╯']
        elif seq in '╔═╗║╚═╝╦':
            return [BoxChar(c) for c in '╔═╗║╦║╚═╝╯']
        elif ord(seq) in range(0x2800, 0x2900):
            return [BoxChar(c) for c in '⢰⠒⡆⢸⢤⡇⠸⠤⠇⡸']

    if len(seq) != 9:
        raise ValueError('Box config should be in len=9')

    return seq


def main():
    parser = argparse.ArgumentParser(prog='cowsay',
                                     description='cowsay')
    parser.add_argument('--margin', default=1, type=int, help='Margin')
    parser.add_argument('--offset', default=4, type=int, help='Left hand side offset of the bubble')
    parser.add_argument('--padding', default=1, type=int, help='Horizontal padding inside the bubble')
    parser.add_argument('--gravity', default='left', choices=('left', 'center', 'right'), help='Gravity')
    parser.add_argument('--tabstop', default=8, type=int, help='tabstop')
    parser.add_argument('--box', default='╭', type=BoxConfig, help='Box drawing characters')

    args = parser.parse_args()

    box = args.box
    padding = args.padding

    def r(ch, width):
        return ch * width

    def space(width):
        return r(' ', width)

    def pad(ch=' '):
        return r(ch, args.padding)

    lines = []
    for line in sys.stdin:
        lines.append(retab(line.rstrip('\n'), tabstop=args.tabstop))

    if not lines:
        sys.exit(1)

    width = max(strwidth(line) for line in lines)

    def puts(line):
        print(space(args.margin) + line)

    cow_offset = -args.offset if args.offset < 0 else 0

    cow_image = [
            space(cow_offset) + '                ' + box[4],
            space(cow_offset) + '           (__) ' + box[9],
            space(cow_offset) + '   _______/(..)',
            space(cow_offset) + ' /(       /(__)',
            space(cow_offset) + '* | w----||',
            space(cow_offset) + '  ||     ||',
            ]
    anchor = cow_image[0].index(str(box[4]))

    puts(space(args.offset) + box[0] + box[1](padding) + box[1](width) + box[1](padding) + box[2])
    for line in lines:
        puts(space(args.offset) + box[3] + space(padding) + ljust(line, width) + space(padding) + box[5])

    bubble_bottom_line = space(args.offset) + box[6] + box[7](padding) + box[7](width) + box[7](padding) + box[8]

    try:
        if bubble_bottom_line[anchor] == box[7]:
            bubble_bottom_line = bubble_bottom_line[:anchor] + box[4] + bubble_bottom_line[anchor+1:]
    except IndexError:
        pass

    puts(bubble_bottom_line)

    for line in cow_image[1:]:
        puts(line)
