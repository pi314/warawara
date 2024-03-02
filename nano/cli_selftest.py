from . import lib_selftest

from . import lib_paint


name_to_module_mapping = {
        'paint': lib_paint
        }


def main(argv):
    lib_selftest.init()

    if not argv:
        module_list = list(name_to_module_mapping.keys())
    else:
        module_list = [name_to_module_mapping[arg] for arg in argv]

    lib_selftest.verbose = True if len(module_list) else False

    for module in module_list:
        module.selftest()

    lib_selftest.print_summary()
