#!/usr/bin/env python3

import argparse

from .lib_tui import getch


def main():
    parser = argparse.ArgumentParser(prog='getch',
                                     description='getch')
    args = parser.parse_args()

    key = getch()
    if isinstance(key, str):
        print(key)
    else:
        try:
            print(key.aliases[0])
        except:
            print(str(key.seq, encoding='utf8'))
