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


class Menu:
    class DoneSelection(Exception):
        pass

    class GiveUpSelection(Exception):
        pass

    def __init__(self, prompt, options, format=None,
                 cursor='>', type='',
                 onkey=None, wrap=False):
        if onkey is not None and not callable(onkey):
            raise TypeError('onkey should be a callable(menu, key, cursor)')

        self.prompt = prompt
        self.cursor = cursor

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

        self.options = [MenuItem(self, opt, format=format, mark=self.mark) for opt in options]

        self.message = ''

        self.onkey = onkey
        self.wrap = wrap

        self.index = 0 # cursor index

    def __len__(self):
        return len(self.options)

    def __getitem__(self, key):
        return self.options[key]

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
            if o.selected or o.is_meta:
                mark = o.mark(self) if callable(o.mark) else o.mark
            else:
                mark = ' ' * len(o.mark)

            Menu.printline('{cursor}{ll}{mark}{rr} {text}'.format(
                cursor=self.cursor if idx == self.index else ' ' * len(self.cursor),
                ll=self.checkbox[0] if not o.is_meta else '{',
                rr=self.checkbox[1] if not o.is_meta else '}',
                mark=mark,
                text=(paints.black / paints.white)(o.text) if idx == self.index else o.text
                ))

        Menu.printline('[' + self.message + ']', end='')

    def handle_key(self, key):
        result = None

        if self.onkey:
            result = self.onkey(menu=self, cursor=self.index, key=key)

        if result is None:
            if key == 'q':
                self.unselect_all()
                self.quit()

            if key == 'enter':
                self.done()

            if key == 'space':
                self[self.index].toggle()

            if key in ('up', 'down', 'home', 'end'):
                self.cursor_move(key)

        elif isinstance(result, str):
            self.message = result

        return result

    def cursor_move(self, what):
        if isinstance(what, int):
            self.index = what

        elif what == 'up':
            self.index -= 1
        elif what == 'down':
            self.index += 1
        elif what == 'home':
            self.index = 0
        elif what == 'end':
            self.index = len(self) - 1

        if self.wrap:
            self.index = (self.index + len(self)) % len(self)
        elif self.index < 0:
            self.index = 0
        elif self.index >= len(self):
            self.index = len(self) - 1

    def selected(self):
        if not self.type:
            return self.options[self.index].obj
        elif self.type == '()':
            return tuple(opt.obj for opt in self.options if opt.selected)
        elif self.type == '[]':
            return [opt.obj for opt in self.options if opt.selected]

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

    def interact(self, suppress=(EOFError, KeyboardInterrupt, BlockingIOError)):
        with HijackStdio():
            with ExceptionSuppressor(suppress):
                while True:
                    self.render()

                    ch = getch()

                    try:
                        action = self.handle_key(ch)

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
    def __init__(self, menu, obj, format=None, mark=None):
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
        self.mark = mark

    def set_meta(self, mark):
        self.is_meta = True
        self.mark = mark

    def toggle(self):
        if self.selected:
            self.unselect()
        else:
            self.select()

    def select(self):
        if self.is_meta:
            return
        self.menu.select(self)

    def unselect(self):
        self.menu.unselect(self)
