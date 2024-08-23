__version__ = '2.0.0'

from .lib_itertools import *
from .lib_math import *
from .lib_paints import *
from .lib_regex import *
from .lib_subproc import *
from .lib_tui import *
from .lib_typesetting import *

itertools = lib_itertools
math = lib_math
paints = lib_paints
regex = lib_regex
subproc = lib_subproc
tui = lib_tui
typesetting = lib_typesetting

from . import bin


def load_cli_entry_points():
    import os
    import importlib

    for f in os.listdir(os.path.dirname(__file__)):
        if f.startswith('bin_') and f.endswith('.py'):
            m = os.path.splitext(f)[0]

            module = importlib.import_module('.' + m, 'smol')
            setattr(bin, m[4:], module)

            del globals()[m]

load_cli_entry_points()

del load_cli_entry_points
