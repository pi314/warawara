import os
from pathlib import Path

from .internal_utils import exporter
export, __all__ = exporter()


@export
def cwd(path=None):
    if path:
        os.chdir(path)

    return Path(os.getcwd())


_dirs = []

@export
class pushd:
    def __init__(self, d):
        _dirs.append(Path(os.getcwd()))
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
