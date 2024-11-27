_open = open
def open(*args, **kwargs):
    if 'encoding' not in kwargs:
        kwargs['encoding'] = 'utf-8'

    if 'errors' not in kwargs:
        kwargs['errors'] = 'backslashreplace'

    f = _open(*args, **kwargs)

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
