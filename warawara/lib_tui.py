import sys

from . import lib_colors as paints

from .lib_itertools import zip_longest, flatten
from .lib_colors import decolor


from .internal_utils import exporter
export, __all__ = exporter()


@export
def strwidth(s):
    import unicodedata
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


@export
def ljust(data, width=None, fillchar=' '):
    return just(just_elem(lpad), data, width, fillchar)


@export
def rjust(data, width=None, fillchar=' '):
    return just(just_elem(rpad), data, width, fillchar)


@export
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

        import itertools
        self.icon_iter = (
                itertools.chain(
                    self.icon_entry,
                    itertools.cycle(self.icon_loop)
                    ),
                iter(self.icon_leave)
                )
        self.icon_head = [None, None]

        import builtins
        self.print_function = builtins.print

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
        import time

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

        import threading
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
    def __init__(self, options, accept_empty=None, abbr=None, sep=None, ignorecase=None):
        if not options:
            accept_empty = True
            abbr = False
            ignorecase = False

        self.accept_empty = alt_if_none(accept_empty, True)
        self.abbr = alt_if_none(abbr, True)
        self.ignorecase = alt_if_none(ignorecase, self.abbr)
        self.sep = alt_if_none(sep, ' / ')

        self.mapping = dict()
        self.options = [o for o in options]

        if self.options:
            if self.accept_empty:
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
        if self.accept_empty and self.ignorecase:
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
        return str(self.selected)

    def __repr__(self):
        return '<warawara.tui.UserSelection selected=[{}]>'.format(self.selected)


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


@export
def prompt(question, options=tuple(),
           accept_empty=True,
           abbr=True,
           ignorecase=None,
           sep=' / ',
           suppress=(EOFError, KeyboardInterrupt)):

    if isinstance(options, str) and ' ' in options:
        options = options.split()

    user_selection = UserSelection(options, accept_empty=accept_empty, abbr=abbr, sep=sep, ignorecase=ignorecase)

    with HijackStdio():
        with ExceptionSuppressor(suppress):
            while user_selection.selected is None:
                print((question + (user_selection.prompt)), end=' ')

                import contextlib
                with contextlib.suppress(ValueError):
                    i = input().strip()
                    user_selection.select(i)

    return user_selection


class Key:
    def __init__(self, seq, *aliases):
        if isinstance(seq, str):
            seq = seq.encode('utf8')

        if not isinstance(seq, bytes):
            raise TypeError('seq should be in type bytes, not {}'.format(type(seq)))

        if not all(isinstance(a, str) for a in aliases):
            raise TypeError('Aliases should be in type str')

        self.seq = seq
        self.aliases = [str(name) for name in aliases]

    def __hash__(self):
        return hash(self.seq)

    def __repr__(self):
        fmt = type(self).__name__ + '({})'
        if self.aliases:
            return fmt.format(self.aliases[0])
        try:
            return fmt.format(self.seq.decode('utf8'))
        except UnicodeError:
            return fmt.format(repr(self.seq))

    def name(self, name):
        if name not in self.aliases:
            self.aliases.append(name)

    def __eq__(self, other):
        if type(self) == type(other):
            return self.seq == other.seq
        elif self.seq == other:
            return True
        elif isinstance(other, str) and self.seq == other.encode('utf8'):
            return True
        else:
            return other in self.aliases


KEY_ESCAPE = Key(b'\033', 'esc', 'escape')
KEY_BACKSPACE = Key(b'\x7f', 'backspace')
KEY_TAB = Key(b'\t', 'tab', 'ctrl-i', 'ctrl+i', '^I')
KEY_ENTER = Key(b'\r', 'enter', 'ctrl-m', 'ctrl+m', '^M')
KEY_SPACE = Key(b' ', 'space')

KEY_UP = Key(b'\033[A', 'up')
KEY_DOWN = Key(b'\033[B', 'down')
KEY_RIGHT = Key(b'\033[C', 'right')
KEY_LEFT = Key(b'\033[D', 'left')

KEY_HOME = Key(b'\033[1~', 'home')
KEY_END = Key(b'\033[4~', 'end')
KEY_PGUP = Key(b'\033[5~', 'pgup', 'pageup')
KEY_PGDN = Key(b'\033[6~', 'pgdn', 'pagedown')

KEY_F1 = Key(b'\033OP', 'F1')
KEY_F2 = Key(b'\033OQ', 'F2')
KEY_F3 = Key(b'\033OR', 'F3')
KEY_F4 = Key(b'\033OS', 'F4')
KEY_F5 = Key(b'\033[15~', 'F5')
KEY_F6 = Key(b'\033[17~', 'F6')
KEY_F7 = Key(b'\033[18~', 'F7')
KEY_F8 = Key(b'\033[19~', 'F8')
KEY_F9 = Key(b'\033[20~', 'F9')
KEY_F10 = Key(b'\033[21~', 'F10')
KEY_F11 = Key(b'\033[23~', 'F11')
KEY_F12 = Key(b'\033[24~', 'F12')

def _register_ctrl_n_keys():
    for c in 'abcdefghjklnopqrstuvwxyz':
        C = c.upper()
        idx = ord(c) - ord('a') + 1
        aliases = ('ctrl-' + c, 'ctrl+' + c, '^' + C)
        globals()['KEY_CTRL_' + C] = Key(chr(idx), *aliases)

_register_ctrl_n_keys()
del _register_ctrl_n_keys


def _export_all_keys():
    for key in globals().keys():
        if key.startswith('KEY_'):
            export(key)

_export_all_keys()
del _export_all_keys


key_table = {}
key_table_reverse = {}

def _init_key_table():
    for k, v in globals().items():
        if not k.startswith('KEY_'):
            continue
        key_table[v.seq] = v

        for alias in v.aliases:
            key_table_reverse[alias] = v

_init_key_table()
del _init_key_table


@export
def register_key(seq, *aliases):
    if isinstance(seq, str):
        seq = seq.encode('utf8')

    if not seq:
        raise ValueError('huh?')

    if seq not in key_table:
        key_table[seq] = Key(seq, *aliases)
        return key_table[seq]

    key = key_table[seq]
    for name in aliases:
        key.name(name)

    return key


@export
def getch(timeout=None, encoding='utf8'):
    import termios, tty
    import os
    import select

    fd = sys.stdin.fileno()
    orig_term_attr = termios.tcgetattr(fd)
    when = termios.TCSADRAIN

    def has_data(t=0):
        return select.select([fd], [], [], t)[0]

    def read_one_byte():
        return os.read(sys.stdin.fileno(), 1)

    try:
        tty.setraw(fd, when=when)

        # Wait for input until timeout
        if not has_data(timeout):
            return None

        acc = b''
        candidate_matches = set(key_table.keys())
        while True:
            acc += read_one_byte()

            if not has_data():
                break

            # Still have change to match in key table
            if candidate_matches:
                # eliminate potential matches
                candidate_matches = set(key_seq for key_seq in candidate_matches if key_seq.startswith(acc))

                # Perfect match, return
                if candidate_matches == {acc}:
                    break

                # multiple prefix matchs: collect more byte
                if candidate_matches:
                    continue

            # Input sequence does not match anything in key table
            # Collect enough bytes to decode at least one unicode char
            try:
                acc.decode(encoding)
                break
            except UnicodeError:
                continue

        if acc in key_table:
            return key_table[acc]

        try:
            return acc.decode(encoding)
        except UnicodeError:
            return acc

    finally:
        termios.tcsetattr(fd, when, orig_term_attr)


class MenuCursor:
    def __init__(self, menu, color):
        self.menu = menu
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

        if self.menu.wrap:
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


class KeyHandler:
    def __init__(self, who, default=None):
        self.who = who
        self.key_handlers = {
                None: [] if default is None else unwrap_one([default])
                }

    def bind(self, key, handler=None):
        if isinstance(key, str):
            key = key_table_reverse.get(key, key)
        elif key is not None and handler is None:
            key, handler = None, key

        handlers = flatten([handler])
        for h in handlers:
            if not callable(h):
                raise ValueError('handler should be a callable', h)

        # Set key/handler binding
        if key not in self.key_handlers:
            self.key_handlers[key] = []
        self.key_handlers[key] += handlers

    def unbind(self, key=None, handler=None):
        if isinstance(key, str):
            key = key_table_reverse.get(key, key)
        elif callable(key) and handler is None:
            key, handler = None, key

        if key not in self.key_handlers:
            return

        if handler is None:
            # Remove all key/handler binding
            self.key_handlers[key] = []
        else:
            # Remove that key/handler binding
            self.key_handlers[key].remove(handler)

    def onkey(self, key):
        handlers = (
                self.key_handlers.get(key, []) +
                self.key_handlers.get(None, [])
                )

        for handler in handlers:
            result = handler(self.who, key=key)
            if result is not None:
                return result


class Menu:
    class DoneSelection(Exception):
        pass

    class GiveUpSelection(Exception):
        pass

    def __init__(self, prompt, options, *, format=None,
                 arrow=None, type=None,
                 onkey=None, wrap=False, color=None):
        # if onkey is not None and not callable(onkey):
        #     raise TypeError('onkey should be a callable(menu, key)')

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
        self.wrap = wrap
        self.key_handler = KeyHandler(self, default=onkey)
        self.crsr = MenuCursor(self, color=color or paints.black/paints.white)

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

    def bind(self, *args, **kwargs):
        self.key_handler.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        self.key_handler.unbind(*args, **kwargs)

    def onkey(self, key):
        result = self[self.crsr].key_handler.onkey(key)
        if isinstance(result, str):
            key = key_table_reverse.get(result, key)
            result = None
        if isinstance(result, Key):
            key = result
            result = None

        if result is None:
            result = self.key_handler.onkey(key)
            if isinstance(result, str):
                key = key_table_reverse.get(result, key)
                result = None
            if isinstance(result, Key):
                key = result
                result = None

        if result is None:
            import termios
            import signal
            term_attr = termios.tcgetattr(sys.stdin.fileno())[6]
            if key == term_attr[termios.VINTR]: # normally ctrl-c
                raise KeyboardInterrupt()
            elif key == term_attr[termios.VSUSP]: # normally ctrl-z
                os.kill(os.getpid(), signal.SIGTSTP)
            elif key == 'q':
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
            return tuple(opt.obj for opt in self.options if opt.selected and not opt.is_phony)
        elif self.type == '[]':
            return [opt.obj for opt in self.options if opt.selected and not opt.is_phony]

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

        elif self.type in ('()', '[]'):
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

    @staticmethod
    def putline(*args, **kwargs):
        args = list(args)
        if args:
            args[0] = '\r\033[K' + args[0]
        else:
            args = ['\r\033[K']
        print(*args, **kwargs)

    def render(self, first):
        if first:
            avail_space = (not(not self.prompt)) + len(self.options) + 1
        else:
            avail_space = shutil.get_terminal_size().lines

        output = []

        if self.prompt:
            output.append(self.prompt)

        for idx, o in enumerate(self.options):
            layer = o if o.arrow else self
            arrow = layer.arrow(layer) if callable(layer.arrow) else layer.arrow

            layer = o if o.checkbox else self
            checkbox = layer.checkbox(layer) if callable(layer.checkbox) else layer.checkbox

            layer = o if o.mark else self
            mark = layer.mark(layer) if callable(layer.mark) else layer.mark

            output.append('{arrow}{ll}{mark}{rr} {text}'.format(
                arrow=arrow if idx == int(self.crsr) else ' ' * len(arrow),
                ll=checkbox[0],
                rr=checkbox[1],
                mark=mark if o.selected or o.is_phony else ' ' * len(mark),
                text=self.cursor.color(o.text) if idx == int(self.crsr) else o.text
                ))

        for line in output[(-avail_space + 1):]:
            Menu.putline(line)

        Menu.putline('[{}]'.format(self.message), end='')

    def interact(self, *, suppress=(EOFError, KeyboardInterrupt, BlockingIOError)):
        with HijackStdio():
            with ExceptionSuppressor(suppress):
                first = True
                while True:
                    self.render(first)
                    first = False

                    ch = getch()

                    try:
                        self.onkey(ch)

                    except Menu.GiveUpSelection:
                        Menu.putline(end='')
                        return

                    except Menu.DoneSelection:
                        s = self.selected()
                        if s is not None:
                            Menu.putline(end='')
                            return s

                    avail_space = shutil.get_terminal_size().lines
                    wipe = min((not(not self.prompt)) + len(self.options), avail_space - 1)
                    print('\r\033[{}A'.format(wipe), end='')


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

        self.key_handler = KeyHandler(self)

        self.selected = False
        self.is_phony = False
        self.arrow = None
        self.checkbox = None
        self.mark = None

    @property
    def phony(self):
        return self.is_phony

    @phony.setter
    def phony(self, value):
        self.is_phony = value
        self.checkbox = '{}' if self.is_phony else None

    def bind(self, *args, **kwargs):
        self.key_handler.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        self.key_handler.unbind(*args, **kwargs)

    def onkey(self, key, handler=None):
        return self.key_handler.onkey(key)

    def toggle(self):
        if self.is_phony:
            return
        if self.selected:
            self.unselect()
        else:
            self.select()

    def select(self):
        if self.is_phony:
            return
        self.menu.select(self)

    def unselect(self):
        if self.is_phony:
            return
        self.menu.unselect(self)

    @property
    def focused(self):
        return self is self.menu[self.menu.cursor]
