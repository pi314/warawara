import os
import sys
import argparse
import shutil

from . import lib_colors as colors


def main():
    prog = sys.argv[0]
    argv = sys.argv[1:]

    term_size = shutil.get_terminal_size()

    parser = argparse.ArgumentParser(description='Remove ANSI color escape codes', prog='decolor')

    args = parser.parse_args(argv)

    for line in sys.stdin:
        print(colors.decolor(line.rstrip('\n')))
