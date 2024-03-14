import sys
import importlib

from os.path import basename


def load_module(module):
    import importlib
    return importlib.import_module('.cli_' + module, 'smol')


def main():
    prog = basename(sys.argv[0])
    sys.argv = sys.argv[1:]

    if not sys.argv:
        import os
        for f in os.listdir(os.path.dirname(__file__)):
            if f.startswith('cli_') and f.endswith('.py'):
                m = os.path.splitext(f[4:])[0]
                print(m)
        exit(1)

    subcmd = sys.argv[0]

    load_module(subcmd).main()
