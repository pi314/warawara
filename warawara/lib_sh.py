import os


__all__ = ['pushd', 'popd', 'dirs']


_dirs = []
class pushd:
    def __init__(self, d):
        _dirs.append(os.getcwd())
        os.chdir(d)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        popd()


def popd():
    if _dirs:
        os.chdir(_dirs.pop())


def dirs():
    return _dirs
