__version__ = '2.0.0'


def check_python_version():
    import sys
    assert sys.version_info.major, sys.version_info.minor >= (3, 7)

check_python_version()
del check_python_version


def load_internal_modules():
    import os
    import importlib
    for f in os.listdir(os.path.dirname(__file__)):
        if f.startswith('lib_') and f.endswith('.py'):
            int_name = os.path.splitext(f)[0]
            ext_name = int_name[4:]
            module = importlib.import_module('.' + int_name, 'smol')

            if '__all__' in module.__dict__:
                attrs = module.__dict__['__all__']
            else:
                attrs = [x for x in module.__dict__ if not x.startswith('_')]

            globals()[ext_name] = globals()[int_name]
            globals().update({attr: getattr(module, attr) for attr in attrs})

            del globals()[int_name]

load_internal_modules()
del load_internal_modules


from . import bin

def load_cli_entry_points():
    import os
    import importlib
    for f in os.listdir(os.path.dirname(__file__)):
        if f.startswith('bin_') and f.endswith('.py'):
            int_name = os.path.splitext(f)[0]
            ext_name = int_name[4:]
            module = importlib.import_module('.' + int_name, 'smol')
            setattr(bin, ext_name, module)
            del globals()[int_name]

load_cli_entry_points()
del load_cli_entry_points
