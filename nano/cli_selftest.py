from . import lib_selftest

from . import lib_paint
from . import lib_rere
from . import lib_cmd


name_to_module_mapping = {
        'paint': lib_paint,
        'rere': lib_rere,
        'cmd': lib_cmd,
        }


def main(argv):
    lib_selftest.init()

    color = lib_selftest.color
    banner = lib_selftest.banner
    sepline = lib_selftest.sepline
    orange = color('38;5;208')

    if not argv:
        module_list = list(name_to_module_mapping.values())
    else:
        module_list = [name_to_module_mapping[arg] for arg in argv]

    lib_selftest.verbose = True if len(module_list) else False

    for idx, module in enumerate(module_list):
        if idx:
            print()

        print(orange(sepline('=')))
        print(orange(module.__name__ + '.selftest()'))
        print(orange(sepline('-')))
        module.selftest()
        print(orange(sepline('-')))

    print()
    lib_selftest.print_summary()
