__version__ = '0.0.1'


from .lib_paint import *
from .lib_rere import *
from .lib_cmd import *

def _load_modules():
    import os
    import importlib
    for f in os.listdir(os.path.dirname(__file__)):
        if f.startswith('cli_') and f.endswith('.py'):
            m = os.path.splitext(f)[0]
            globals()[m] = importlib.import_module('.' + m, 'nano')

_load_modules()
