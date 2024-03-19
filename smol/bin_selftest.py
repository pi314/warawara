import os
import sys

from . import selftest

from . import paints
from . import regex
from . import subproc


def main():
    prog = sys.argv[0]
    argv = sys.argv[1:]

    selftest.init()

    color = selftest.color
    banner = selftest.banner
    sepline = selftest.sepline
    orange = color('38;5;208')

    if not argv:
        module_list = []
        for f in os.listdir(os.path.dirname(__file__)):
            if f.startswith('__'): continue
            if f.startswith('bin_'): continue
            if not f.endswith('.py'): continue

            m = os.path.splitext(f)[0]
            if m in globals():
                module_list.append(m)
    else:
        module_list = argv
        error = False
        for module_name in module_list:
            if module_name not in globals():
                print('Unknown module: {}'.format(module_name), file=sys.stderr)
                error = True
        if error:
            exit(1)

    for idx, module_name in enumerate(module_list):
        if idx:
            print()

        module = globals()[module_name]

        if not hasattr(module, 'selftest'):
            continue

        print(orange(sepline('=')))
        print(orange(module.__name__ + '.selftest()'))
        print(orange(sepline('-')))
        module.selftest()
        print(orange(sepline('-')))

    print()
    selftest.print_summary()
