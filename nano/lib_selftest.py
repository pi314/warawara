import inspect


verbose = True


def init():
    global color
    global pass_tag
    global fail_tag
    global fail_list
    global pass_list

    color = lambda x: lambda s: f'\033[{x}m{s}\033[m'

    pass_tag = color(32)('[pass]')
    fail_tag = color(31)('[fail]')

    fail_list = dict()
    pass_list = dict()


def hrepr(obj):
    if obj is None:
        return color(36)('None')

    if isinstance(obj, int):
        return color(35)(f'{obj}')

    if isinstance(obj, list):
        return '[' + ', '.join(hrepr(o) for o in obj) + ']'

    if isinstance(obj, dict):
        return '{' + ', '.join(hrepr(key) + ': ' + hrepr(value) for key, value in obj.items())+ '}'

    import re
    robj = repr(obj)

    if isinstance(obj, str):
        return color(35)(re.sub(
            r'(\\\w+)',
            r'\033[31m\1\033[35m',
            robj))

    # obj
    m = re.match(r'^(\w+)\((.*)\)$', robj)
    if m:
        import ast
        typename = m.group(1)
        arg_list = []
        for token in m.group(2).split(', '):
            if '=' in token:
                a, b = token.split('=')
                try:
                    b = ast.literal_eval(b)
                except ValueError:
                    pass

                arg_list.append(f'{a}={hrepr(b)}')

            else:
                arg_list.append(token)

        return f'{typename}({", ".join(arg_list)})'

    return robj


def section(title):
    frame = inspect.stack()[1]
    filename = frame.filename
    lineno = frame.lineno
    print()
    print(color(36)(f'[section] {title} @({filename}:{lineno})'))


def EXPECT_EQ(a, b):
    frame = inspect.stack()[1]
    filename = frame.filename
    lineno = frame.lineno

    cond_repr = f'{hrepr(a)} == {hrepr(b)}'
    if a == b:
        print(pass_tag, cond_repr)
        if filename not in pass_list:
            pass_list[filename] = []
        pass_list[filename].append((frame, cond_repr))
        return

    print(fail_tag, cond_repr)

    if filename not in fail_list:
        fail_list[filename] = []
    fail_list[filename].append((frame, cond_repr))


def print_summary():
    print('-' * 79)
    print('Failed tests:')
    for filename in fail_list:
        for frame, cond_repr in fail_list[filename]:
            print()
            print(fail_tag, cond_repr)
            print(f'    At {frame.filename}:{frame.lineno}')

    print('-' * 79)
    print('Summary:')
    for filename in fail_list:
        print(fail_tag, f'{len(fail_list[filename])} failed')

    for filename in pass_list:
        print(pass_tag, f'{len(pass_list[filename])} passed')
