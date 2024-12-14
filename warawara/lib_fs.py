import builtins

from .internal_utils import exporter
export, __all__ = exporter()


@export
def open(*args, **kwargs):
    if 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'

    if 'errors' not in kwargs:
        kwargs['errors'] = 'backslashreplace'

    f = builtins.open(*args, **kwargs)

    def writeline(line=''):
        s = str(line)
        f.write(s + ('' if s.endswith('\n') else '\n'))

    def writelines(lines=[]):
        for line in lines:
            writeline(line)

    def readlines():
        return [line.rstrip('\n') for line in f]

    f.writeline = writeline
    f.writelines = writelines
    f.readlines = readlines

    return f


@export
def fsorted(iterable, key=None):
    import re
    def filename_as_key(name):
        def int_or_not(x):
            if x and x[0] in '1234567890':
                return int(x)
            return x
        return tuple(int_or_not(x) for x in re.split(r'([0-9]+)', name))

    if key is None:
        sort_key = filename_as_key
    else:
        sort_key = lambda x: filename_as_key(key(x))

    return sorted(iterable, key=sort_key)
