from . import lib_selftest

from . import lib_paint
from . import lib_rere


name_to_module_mapping = {
        'paint': lib_paint,
        'rere': lib_rere,
        }


def main(argv):
    lib_selftest.init()

    if not argv:
        module_list = list(name_to_module_mapping.values())
    else:
        module_list = [name_to_module_mapping[arg] for arg in argv]

    lib_selftest.verbose = True if len(module_list) else False

    for module in module_list:
        module.selftest()

    lib_selftest.print_summary()
