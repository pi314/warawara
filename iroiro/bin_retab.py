#!/usr/bin/env python3

import argparse
import sys

from .lib_tui import retab


def main():
    parser = argparse.ArgumentParser(prog='retab',
                                     description='retab')
    parser.add_argument('--tabstop', default=4, type=int, help='tabstop')
    parser.add_argument('--listchars', default=' ', type=str, help='listchars')

    args = parser.parse_args()

    for line in sys.stdin:
        print(retab(line.rstrip('\n'), tabstop=args.tabstop, listchars=args.listchars))


if __name__ == '__main__':
    main()
