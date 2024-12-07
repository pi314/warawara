import os
from pathlib import Path

from .internal_utils import exporter
export, __all__ = exporter()


@export
def cwd(path=None):
    if path:
        os.chdir(path)
    return Path.cwd()


_dirs = []

@export
class pushd:
    def __init__(self, d):
        _dirs.append(Path.cwd())
        os.chdir(d)

    def __enter__(self):
        return

    def __exit__(self, exc_type, exc_value, traceback):
        popd()


@export
def popd():
    if _dirs:
        os.chdir(_dirs.pop())


@export
def dirs():
    return list(_dirs) + [cwd()]


@export
def home():
    return Path.home()


@export
def shrinkuser(path):
    path = str(path)
    trailing_slash = '/' if path.endswith('/') else ''

    import os.path
    path = path.rstrip('/') + '/'
    homepath = os.path.expanduser('~').rstrip('/') + '/'
    if path.startswith(homepath):
        ret = os.path.join('~', path[len(homepath):])
    else:
        ret = path
    return ret.rstrip('/') + trailing_slash
