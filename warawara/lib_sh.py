import os
from pathlib import Path


__all__ = ['cwd', 'pushd', 'popd', 'dirs']


def cwd(path=None):
    if path:
        os.chdir(path)

    return Path(os.getcwd())


_dirs = []
class pushd:
    def __init__(self, d):
        _dirs.append(Path(os.getcwd()))
        os.chdir(d)

    def __enter__(self):
        return Path(self)

    def __exit__(self, exc_type, exc_value, traceback):
        popd()


def popd():
    if _dirs:
        os.chdir(_dirs.pop())


def dirs():
    return list(_dirs) + [cwd()]
