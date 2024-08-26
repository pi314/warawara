import contextlib
import itertools
import sys
import threading
import time
import enum


from . import lib_paints as paints


__all__ = ['ThreadedSpinner', 'prompt']


class ThreadedSpinner:
    def __init__(self, *icon, delay=0.1):
        if not icon:
            self.icon_entry = '⠉⠛⠿⣿⠿⠛⠉⠙'
            self.icon_loop = '⠹⢸⣰⣤⣆⡇⠏⠛'
            self.icon_leave = '⣿'
        elif len(icon) == 1:
            self.icon_entry = tuple()
            self.icon_loop = icon
            self.icon_leave = '.'
        elif len(icon) == 2:
            self.icon_entry = icon[0]
            self.icon_loop = icon[1]
            self.icon_leave = '.'
        elif len(icon) == 3:
            self.icon_entry = icon[0]
            self.icon_loop = icon[1]
            self.icon_leave = icon[2]
        else:
            raise ValueError('Invalid value: ' + repr(icon))

        ok = True
        for name, icon in (('entry', self.icon_entry), ('loop', self.icon_loop), ('leave', self.icon_leave)):
            if isinstance(icon, str):
                ok = True
            elif isinstance(icon, (tuple, list)) and all(isinstance(c, str) for c in icon):
                ok = True
            else:
                raise ValueError('Invalid value of icon[{}]: {}'.format(name, icon))

        self.delay = delay
        self.is_end = False
        self.thread = None
        self._text = ''
        self.icon_iter = (
                itertools.chain(
                    self.icon_entry,
                    itertools.cycle(self.icon_loop)
                    ),
                iter(self.icon_leave)
                )
        self.icon_head = [None, None]

        self.print_function = print

    def __enter__(self):
        if self.thread:
            return self

        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()

    @property
    def icon(self):
        idx = self.is_end
        if self.icon_head[idx] is None:
            self.icon_head[idx] = next(self.icon_iter[idx])
        return self.icon_head[idx]

    def text(self, *args):
        if not args:
            return self._text

        self._text = ' '.join(str(a) for a in args)
        if self.thread:
            self.refresh()

    def refresh(self):
        self.print_function('\r' + self.icon + '\033[K ' + self._text, end='')

    def animate(self):
        while not self.is_end:
            self.refresh()
            time.sleep(self.delay)
            self.icon_head[0] = next(self.icon_iter[0])

        try:
            while True:
                self.refresh()
                self.icon_head[1] = next(self.icon_iter[1])
                time.sleep(self.delay)
        except StopIteration:
            pass

        self.print_function()

    def start(self):
        if self.thread:
            return

        self.thread = threading.Thread(target=self.animate)
        self.thread.daemon = True
        self.thread.start()

    def end(self, wait=True):
        self.is_end = True
        if wait:
            self.join()

    def join(self):
        self.thread.join()


def alt_if_none(A, B):
    if A is None:
        return B
    return A


class UserSelection:
    def __init__(self, options, accept_cr=None, abbr=None, sep=None, ignorecase=None):
        if not options:
            accept_cr = True # carriage return
            abbr = False
            ignorecase = False

        self.accept_cr = alt_if_none(accept_cr, True)
        self.abbr = alt_if_none(abbr, True)
        self.ignorecase = alt_if_none(ignorecase, self.abbr)
        self.sep = alt_if_none(sep, ' / ')

        self.mapping = dict()
        self.options = [o for o in options]

        if self.options:
            if self.accept_cr:
                self.mapping[''] = self.options[0]

            for opt in self.options:
                for o in (opt,) + ((opt[0],) if self.abbr else tuple()):
                    self.mapping[o.lower() if self.ignorecase else o] = opt

        self.selected = None

    def select(self, o=''):
        if self.ignorecase:
            o = o.lower()

        if not self.options:
            self.selected = o
            return

        if o not in self.mapping:
            raise ValueError('Invalid option: ' + o)

        self.selected = o

    @property
    def prompt(self):
        if not self.options:
            return ''

        opts = [o for o in self.options]
        if self.accept_cr and self.ignorecase:
            opts[0] = opts[0].capitalize()

        if self.abbr:
            return ' [' + self.sep.join('({}){}'.format(o[0], o[1:]) for o in opts) + ']'
        else:
            return ' [' + self.sep.join(opts) + ']'

    def __eq__(self, other):
        if self.ignorecase and other is not None:
            other = other.lower()

        if self.selected == other:
            return True

        if self.selected in self.mapping:
            return self.mapping[self.selected] == self.mapping.get(other)

        return False

    def __str__(self):
        return self.selected

    def __repr__(self):
        return '<smol.tui.UserSelection selected=[{}]>'.format(self.selected)


class HijackStdio:
    def __init__(self, replace_with='/dev/tty'):
        self.replace_with = replace_with

    def __enter__(self):
        self.stdin_backup = sys.stdin
        self.stdout_backup = sys.stdout
        self.stderr_backup = sys.stderr

        sys.stdin = open(self.replace_with)
        sys.stdout = open(self.replace_with, 'w')
        sys.stderr = open(self.replace_with, 'w')

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

        sys.stdin = self.stdin_backup
        sys.stdout = self.stdout_backup
        sys.stderr = self.stderr_backup


class ExceptionSuppressor:
    def __init__(self, *exc_group):
        if isinstance(exc_group[0], tuple):
            self.exc_group = exc_group[0]
        else:
            self.exc_group = exc_group

    def __enter__(self, *exc_group):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type in (EOFError, KeyboardInterrupt):
            print()
        return exc_type in self.exc_group


def prompt(question, options=tuple(),
           accept_cr=None,
           abbr=None,
           ignorecase=None,
           sep=None,
           suppress=(EOFError, KeyboardInterrupt)):

    if isinstance(options, str) and ' ' in options:
        options = options.split()

    user_selection = UserSelection(options, accept_cr=accept_cr, abbr=abbr, sep=sep, ignorecase=ignorecase)

    with HijackStdio():
        with ExceptionSuppressor(suppress):
            while user_selection.selected is None:
                print((question + (user_selection.prompt)), end=' ')

                with contextlib.suppress(ValueError):
                    i = input().strip()
                    user_selection.select(i)

    return user_selection


special_key_table = {
        '\033[A':   'up',
        '\033[B':   'down',
        '\033[C':   'right',
        '\033[D':   'left',
        '\033':     'esc',
        '\033[1~':  'home',
        '\033[4~':  'end',
        '\033[5~':  'pgup',
        '\033[6~':  'pgdn',
        '\x7f':     'backspace',
        '\n':       'enter',
        '\t':       'tab',
        ' ':        'space',
        }


def getch(timeout=None, alias=True):
    import termios, tty
    import os
    import time
    import select

    fd = sys.stdin.fileno()
    orig = termios.tcgetattr(fd)

    def has_data(t=0):
        return select.select([fd], [], [], t)[0]

    def read_one_byte():
        return os.read(sys.stdin.fileno(), 1).decode('utf8')

    try:
        tty.setcbreak(fd)  # or tty.setraw(fd) if you prefer raw mode's behavior.

        # Wait for input until timeout
        if not has_data(timeout):
            return None

        acc = ''
        while True:
            acc += read_one_byte()

            if not has_data():
                return special_key_table.get(acc, acc) if alias else acc

            if acc != '\033' and acc in special_key_table:
                return special_key_table[acc] if alias else acc

            # prefix match: collectmore char
            if any(key_seq for key_seq in special_key_table.keys() if key_seq.startswith(acc)):
                continue

            return acc

    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, orig)


class MenuType(enum.Enum):
    SELECT = enum.auto()
    RADIO = enum.auto()
    CHECKBOX = enum.auto()


class MenuOperation(enum.Enum):
    QUIT = enum.auto()
    SELECT = enum.auto()
    TOGGLE = enum.auto()
    CURSOR_UP = enum.auto()
    CURSOR_DOWN = enum.auto()
    CURSOR_HOME = enum.auto()
    CURSOR_END = enum.auto()


def _default_onkey(key, cursor):
    if key == 'q':
        return MenuOperation.QUIT

    if key == 'enter':
        return MenuOperation.SELECT

    if key == 'space':
        return MenuOperation.TOGGLE

    if key == 'up':
        return MenuOperation.CURSOR_UP

    if key == 'down':
        return MenuOperation.CURSOR_DOWN

    if key == 'home':
        return MenuOperation.CURSOR_HOME

    if key == 'end':
        return MenuOperation.CURSOR_END


class MenuItem:
    def __init__(self, obj, format):
        self.obj = obj
        self.text = format(obj)
        self.selected = False


def menu(question, options, format=str, type=MenuType.SELECT, wrap=False,
         onkey=_default_onkey,
         suppress=(EOFError, KeyboardInterrupt, BlockingIOError)):
    user_options = options

    if not callable(onkey):
        raise TypeError('onkey should be a callable(key, cursor)')

    if type == MenuType.SELECT:
        cursor_format = ['  ', '> ']
    elif type == MenuType.RADIO:
        cursor_format = ['({selected}) ', '({selected}> ']
    elif type == MenuType.CHECKBOX:
        cursor_format = ['[{selected}] ', '[{selected}> ']
    else:
        raise ValueError('Invalid menu type: {}'.format(repr(type)))

    options = [MenuItem(opt, format) for opt in user_options]

    def printline(*args, **kwargs):
        args = list(args)
        if args:
            args[0] = '\r\033[K' + args[0]
        else:
            args = ['\r\033[K']
        print(*args, **kwargs)

    with HijackStdio():
        with ExceptionSuppressor(suppress):
            cursor = 0
            message = ''
            while True:
                if question:
                    printline(question)

                for idx, o in enumerate(options):
                    text = (paints.black / paints.white)(o.text) if idx == cursor else o.text
                    printline((cursor_format[idx == cursor] + text).format(selected='V' if o.selected else ' '))

                printline('[' + message + ']', end='')

                ch = getch()

                action = onkey(key=ch, cursor=options[cursor])
                if action is None:
                    action = _default_onkey(key=ch, cursor=options[cursor])

                if isinstance(action, str):
                    message = action

                elif action == MenuOperation.QUIT:
                    printline(end='')
                    return

                elif action == MenuOperation.SELECT:
                    printline(end='')
                    if type == MenuType.RADIO:
                        return tuple(opt.obj for opt in options if opt.selected)
                    elif type == MenuType.CHECKBOX:
                        return [opt.obj for opt in options if opt.selected]
                    else: # MenuType.SELECT
                        return options[cursor].obj

                elif action == MenuOperation.TOGGLE:
                    if type in (MenuType.SELECT, MenuType.RADIO):
                        for opt in options:
                            opt.selected = False

                    options[cursor].selected = not options[cursor].selected

                elif action == MenuOperation.CURSOR_UP:
                    cursor = cursor - 1

                elif action == MenuOperation.CURSOR_DOWN:
                    cursor = cursor + 1

                elif action == MenuOperation.CURSOR_HOME:
                    cursor = 0

                elif action == MenuOperation.CURSOR_END:
                    cursor = len(options) - 1

                if wrap:
                    cursor = (cursor + len(options)) % len(options)
                elif cursor < 0:
                    cursor = 0
                elif cursor >= len(options):
                    cursor = len(options) - 1

                printline('{' + message + '}', end='')
                print('\r\033[{}A'.format(len(options) + 1), end='')
