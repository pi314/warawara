import contextlib
import enum
import itertools
import re
import sys
import threading
import time
import unicodedata

from . import lib_paints as paints

from .lib_itertools import zip_longest
from .lib_paints import decolor


__all__ = ['strwidth', 'ljust', 'rjust']
__all__ += ['ThreadedSpinner', 'prompt']


def strwidth(s):
    return sum((1 + (unicodedata.east_asian_width(c) in 'WF')) for c in decolor(s))


def lpad(text, padding):
    return text + padding


def rpad(text, padding):
    return padding + text


def just_elem(func):
    def wrapper(elem, width, fillchar):
        row, col, text = elem
        padding = (width - strwidth(text)) * fillchar(row=row, col=col, text=text)
        return func(text, padding)
    return wrapper


def just_generator(just_func, data, width, fillchar):
    for row, vector in enumerate(data):
        if isinstance(width, int):
            width = (width,) * len(vector)
        yield tuple(
                just_func((row, col, text), w, fillchar)
                for col, (text, w) in enumerate(zip_longest(vector, width[:len(vector)], fillvalues=('', 0)))
                )


def just(just_func, data, width, fillchar):
    if not callable(fillchar):
        _fillchar = fillchar
        fillchar = lambda row, col, text: _fillchar

    if isinstance(data, str):
        return just_func((0, 0, data), width, fillchar)

    if width:
        if isinstance(data, (tuple, list)):
            t = type(data)
        else:
            t = lambda x: x
        return t(just_generator(just_func, data, width, fillchar))

    maxwidth = []
    for vector in data:
        maxwidth = [
                max(w, strwidth(text))
                for text, w in zip_longest(vector, maxwidth, fillvalues=('', 0))
                ]

    return [
            tuple(
                just_func((row, col, text), w, fillchar)
                for col, (text, w) in enumerate(zip_longest(vector, maxwidth, fillvalues=('', 0)))
                )
            for row, vector in enumerate(data)
            ]


def ljust(data, width=None, fillchar=' '):
    return just(just_elem(lpad), data, width, fillchar)


def rjust(data, width=None, fillchar=' '):
    return just(just_elem(rpad), data, width, fillchar)



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


class Key:
    def __init__(self, seq, *aliases):
        if not aliases:
            raise ValueError('At least one alias should be specified')

        self.seq = seq
        self.aliases = [str(name) for name in aliases]

    def __hash__(self):
        return hash(self.seq)

    def __repr__(self):
        return self.aliases[0]

    def name(self, name):
        if name not in self.aliases:
            self.aliases.append(name)

    def __eq__(self, other):
        if type(self) == type(other):
            return self.seq == other.seq
        else:
            return other == self.seq or other in self.aliases


KEY_UP = Key('\033[A', 'up')
KEY_DOWN = Key('\033[B', 'down')
KEY_RIGHT = Key('\033[C', 'right')
KEY_LEFT = Key('\033[D', 'left')
KEY_ESCAPE = Key('\033', 'esc', 'escape')
KEY_HOME = Key('\033[1~', 'home')
KEY_END = Key('\033[4~', 'end')
KEY_PGUP = Key('\033[5~', 'pgup', 'pageup')
KEY_PGDN = Key('\033[6~', 'pgdn', 'pagedown')
KEY_BACKSPACE = Key('\x7f', 'backspace')
KEY_TAB = Key('\t', 'tab')
KEY_ENTER = Key('\n', 'enter')
KEY_SPACE = Key(' ', 'space')
KEY_F1 = Key('\033OP', 'f1')
KEY_F2 = Key('\033OQ', 'f2')
KEY_F3 = Key('\033OR', 'f3')
KEY_F4 = Key('\033OS', 'f4')
KEY_F5 = Key('\033[15~', 'f5')
KEY_F6 = Key('\033[17~', 'f6')
KEY_F7 = Key('\033[18~', 'f7')
KEY_F8 = Key('\033[19~', 'f8')
KEY_F9 = Key('\033[20~', 'f9')
KEY_F10 = Key('\033[21~', 'f10')
KEY_F11 = Key('\033[23~', 'f11')
KEY_F12 = Key('\033[24~', 'f12')

__all__ += [key for key in globals().keys() if key.startswith('KEY_')]


key_table = {
        v.seq : v
        for k,v in globals().items()
        if k.startswith('KEY_')
        }


__all__ += ['register_key']
def register_key(seq, *aliases):
    if not seq or not isinstance(seq, str):
        raise ValueError('huh?')

    if seq not in key_table:
        key_table[seq] = Key(seq, *aliases)
        return key_table[seq]

    key = key_table[seq]
    for name in aliases:
        key.name(name)

    return key


def getch(timeout=None):
    import termios, tty
    import os
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
                return key_table.get(acc, acc)

            if acc != '\033' and acc in key_table:
                return key_table[acc]

            # prefix match: collect more char
            if any(key_seq for key_seq in key_table.keys() if key_seq.startswith(acc)):
                continue

            return acc

    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, orig)


class MenuCursor:
    def __init__(self, menu, wrap, color):
        self.menu = menu
        self.wrap = wrap
        self.index = 0
        self.color = color

    def __int__(self):
        return self.index

    def __eq__(self, what):
        if isinstance(what, int):
            l = len(self.menu)
            return self.index == (what + l) % l
        return self.menu[self.index].obj == what

    def move(self, where):
        if isinstance(where, int):
            self.index = where
        else:
            for idx, item in enumerate(self.menu):
                if item.obj == where:
                    self.index = idx
                    break

        if self.wrap:
            self.index = (self.index + len(self.menu)) % len(self.menu)
        elif self.index < 0:
            self.index = 0
        elif self.index >= len(self.menu):
            self.index = len(self.menu) - 1

    def __iadd__(self, what):
        self.index += what

    def __isub__(self, what):
        self.index -= what

    def __getattr__(self, what):
        return getattr(self.menu[self.index], what)


class Menu:
    class DoneSelection(Exception):
        pass

    class GiveUpSelection(Exception):
        pass

    def __init__(self, prompt, options, *, format=None,
                 arrow=None, type=None,
                 onkey=None, wrap=False, color=None):
        if onkey is not None and not callable(onkey):
            raise TypeError('onkey should be a callable(menu, cursor, key)')

        self.prompt = prompt
        self.arrow = arrow or '>'

        if type in (None, 'default', 'select'):
            type = ''
        elif type.lower() == 'radio':
            type = '(*)'
        elif type.lower() == 'checkbox':
            type = '[*]'

        if len(type) < 2:
            self.checkbox = ('', '')
            self.type = ''
            self.mark = ''
        else:
            self.checkbox = (type[0], type[-1])
            self.type = self.checkbox[0] + self.checkbox[1]
            self.mark = type[1:-1] or '*'

        self.options = [MenuItem(self, opt, format=format) for opt in options]
        self.message = ''
        self.onkey = onkey
        self.crsr = MenuCursor(self, wrap=wrap,
                               color=color or paints.black/paints.white)

    def __len__(self):
        return len(self.options)

    def __getitem__(self, key):
        if key == self.cursor:
            return self.options[int(key)]
        return self.options[key]

    @property
    def cursor(self):
        return self.crsr

    @cursor.setter
    def cursor(self, where):
        self.crsr.move(where)

    @staticmethod
    def printline(*args, **kwargs):
        args = list(args)
        if args:
            args[0] = '\r\033[K' + args[0]
        else:
            args = ['\r\033[K']
        print(*args, **kwargs)

    def render(self):
        if self.prompt:
            Menu.printline(self.prompt)

        for idx, o in enumerate(self.options):
            layer = o if o.arrow else self
            arrow = layer.arrow(layer) if callable(layer.arrow) else layer.arrow

            layer = o if o.checkbox else self
            checkbox = layer.checkbox(layer) if callable(layer.checkbox) else layer.checkbox

            layer = o if o.mark else self
            mark = layer.mark(layer) if callable(layer.mark) else layer.mark

            Menu.printline('{arrow}{ll}{mark}{rr} {text}'.format(
                arrow=arrow if idx == int(self.crsr) else ' ' * len(arrow),
                ll=checkbox[0],
                rr=checkbox[1],
                mark=mark if o.selected or o.is_meta else ' ' * len(mark),
                text=self.cursor.color(o.text) if idx == int(self.crsr) else o.text
                ))

        Menu.printline('[{}]'.format(self.message), end='')

    def handle_key(self, key):
        result = None

        if self[self.crsr].onkey:
            result = self[self.crsr].onkey(item=self[self.crsr], key=key)
            if isinstance(result, str):
                key = result
                result = None

        if result is None and self.onkey:
            result = self.onkey(menu=self, key=key)
            if isinstance(result, str):
                key = result
                result = None

        if result is None:
            if key == 'q':
                self.unselect_all()
                self.quit()
            elif key == 'enter':
                self.done()
            elif key == 'space':
                self[int(self.crsr)].toggle()
            elif key == 'up':
                self.cursor -= 1
            elif key == 'down':
                self.cursor += 1
            elif key == 'home':
                self.cursor = 0
            elif key == 'end':
                self.cursor = -1

        return result

    def selected(self):
        if not self.type:
            return self.options[int(self.crsr)].obj
        elif self.type == '()':
            return tuple(opt.obj for opt in self.options if opt.selected and not opt.is_meta)
        elif self.type == '[]':
            return [opt.obj for opt in self.options if opt.selected and not opt.is_meta]

    def select(self, opt):
        if not self.type:
            return

        elif self.type == '()':
            self.unselect_all()
            opt.selected = True

        elif self.type == '[]':
            opt.selected = True

    def unselect(self, opt):
        if not self.type:
            return

        elif self.type == '()':
            opt.selected = False

        elif self.type == '[]':
            opt.selected = False

    def select_all(self):
        if not self.type:
            return

        elif self.type == '()':
            return

        elif self.type == '[]':
            for opt in self.options:
                opt.select()

    def unselect_all(self):
        for opt in self.options:
            opt.unselect()

    def done(self):
        raise Menu.DoneSelection()

    def quit(self):
        raise Menu.GiveUpSelection()

    def interact(self, *, suppress=(EOFError, KeyboardInterrupt, BlockingIOError)):
        with HijackStdio():
            with ExceptionSuppressor(suppress):
                while True:
                    self.render()

                    ch = getch()

                    try:
                        self.handle_key(ch)

                    except Menu.GiveUpSelection:
                        Menu.printline(end='')
                        return

                    except Menu.DoneSelection:
                        s = self.selected()
                        if s is not None:
                            Menu.printline(end='')
                            return s

                    print('\r\033[{}A'.format(len(self.options) + 1), end='')


class MenuItem:
    def __init__(self, menu, obj, *, format=None):
        self.menu = menu
        self.obj = obj
        if callable(format):
            self.text = format(obj)
        elif isinstance(format, str):
            self.text = format.format(option=obj)
        else:
            try:
                self.text = str(obj)
            except:
                self.text = repr(obj)

        self.selected = False
        self.is_meta = False
        self.arrow = None
        self.checkbox = None
        self.mark = None
        self.onkey = None

    def set_meta(self, *, mark=None, arrow=None, checkbox=None, onkey=None):
        self.is_meta = True
        self.arrow = arrow or self.arrow
        self.checkbox = checkbox or self.checkbox or '{}'
        self.mark = mark or self.mark
        self.onkey = onkey

    def toggle(self):
        if self.is_meta:
            return
        if self.selected:
            self.unselect()
        else:
            self.select()

    def select(self):
        if self.is_meta:
            return
        self.menu.select(self)

    def unselect(self):
        if self.is_meta:
            return
        self.menu.unselect(self)

    @property
    def focused(self):
        return self is self.menu[self.menu.cursor]
