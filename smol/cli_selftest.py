import sys


from . import lib_selftest

from . import lib_paint
from . import lib_rere
from . import lib_cmd


name_to_module_mapping = {
        'paint': lib_paint,
        'rere': lib_rere,
        'cmd': lib_cmd,
        }


def main():
    prog = sys.argv[0]
    argv = sys.argv[1:]

    lib_selftest.init()

    color = lib_selftest.color
    banner = lib_selftest.banner
    sepline = lib_selftest.sepline
    orange = color('38;5;208')

    import os
    import importlib
    modules = {}
    for f in os.listdir(os.path.dirname(__file__)):
        if f.startswith('lib_') and f.endswith('.py'):
            m = os.path.splitext(f[4:])[0]
            modules[m] = importlib.import_module('.lib_' + m, 'smol')

    if not argv:
        module_list = list(modules.values())
    else:
        module_list = [modules[arg] for arg in argv]

    for idx, module in enumerate(module_list):
        if idx:
            print()

        if not hasattr(module, 'selftest'):
            continue

        print(orange(sepline('=')))
        print(orange(module.__name__ + '.selftest()'))
        print(orange(sepline('-')))
        module.selftest()
        print(orange(sepline('-')))

    print()
    lib_selftest.print_summary()
