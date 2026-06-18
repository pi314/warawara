import unittest
import threading
import queue

from collections import UserList

from .internal_utils import exporter
export, __all__ = exporter()

from .lib_lang import getter, setter
from .lib_regex import rere
from .lib_colors import color


__unittest = True

# Keep a Thread reference because it would be patched in testcase
Thread = threading.Thread
Event = threading.Event


@export
class Checkpoint:
    def __init__(self, testcase):
        self.testcase = testcase
        self.checkpoint = threading.Event()

    def set(self):
        self.checkpoint.set()

    def clear(self):
        self.checkpoint.clear()

    def wait(self):
        self.checkpoint.wait()

    def is_set(self):
        return self.checkpoint.is_set()

    def verify(self, is_set=True):
        self.testcase.eq(
                self.checkpoint.is_set(),
                is_set,
                'Checkpoint was' + (' ' if self.checkpoint.is_set() else ' not ') + 'set')
        self.checkpoint.clear()

    def check(self, *args, **kwargs):
        self.verify(*args, **kwargs)

    def __bool__(self):
        return self.is_set()


@export
class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.almost_eq = self.assertAlmostEqual
        self.ne = self.assertNotEqual
        self.le = self.assertLessEqual
        self.lt = self.assertLess
        self.ge = self.assertGreaterEqual
        self.gt = self.assertGreater
        self.true = self.assertTrue
        self.false = self.assertFalse
        self.raises = self.assertRaises

    def setUp(self):
        super().setUp()
        self.fake_time = FakeTime(testcase=self)
        self.fake_time.setup()
        if hasattr(self, 'setup'):
            self.setup()

    def tearDown(self):
        self.fake_time.teardown()
        if hasattr(self, 'teardown'):
            self.teardown()
        super().tearDown()

    def eq(self, first, second, msg=None):
        if (not isinstance(first, (list, tuple, UserList)) or
            not isinstance(second, (list, tuple, UserList)) or
            (type(first) is tuple) != (type(second) is tuple) or
            first == second):
            return self.assertEqual(first, second, msg)

        else:
            from difflib import SequenceMatcher
            try:
                m = SequenceMatcher(None, first, second, False)
                opcodes = m.get_opcodes()
            except TypeError:
                m = SequenceMatcher(None, [repr(i) for i in first], [repr(i) for i in second], False)
                opcodes = m.get_opcodes()

            msg = ['Lists not equal:']
            msg.append('[')
            for tag, i1, i2, j1, j2 in opcodes:
                if tag == 'equal':
                    ops = ((' ', first[i1:i2]),)
                elif tag == 'insert':
                    ops = (('+', second[j1:j2]),)
                elif tag == 'delete':
                    ops = (('-', first[i1:i2]),)
                else: # tag == 'replace'
                    ops = (
                            ('-', first[i1:i2]),
                            ('+', second[j1:j2])
                            )
                for deco, items in ops:
                    msg += [f'{deco} {repr(item)},' for item in items]

            msg.append(']')
            raise AssertionError('\n'.join(msg))

    def contains(self, a, b):
        self.assertIn(b, a)

    def contains_no(self, a, b):
        self.assertNotIn(b, a)

    def isinstance(self, first, second):
        return self.true(isinstance(first, second))

    def checkpoint(self):
        return Checkpoint(self)

    class run_in_thread:
        def __init__(self, func, args=tuple(), kwargs=dict()):
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.thread = None

        def __enter__(self, *args):
            if self.thread is not None:
                raise RuntimeError('Thread objects cannot be reused')
            self.thread = threading.Thread(target=self.func, args=self.args, kwargs=self.kwargs)
            self.thread.daemon = True
            self.thread.start()

        def __exit__(self, exc_type, exc_value, traceback):
            self.thread.join()

    def patch(self, name, side_effect):
        patcher = unittest.mock.patch(name, side_effect=side_effect)
        patcher.start()
        def patcher_stop():
            try:
                patcher.stop()
            except RuntimeError: # pragma: no cover
                pass
        self.addCleanup(patcher_stop)
        return patcher


@export
class RunMocker:
    def __init__(self):
        self.rules = {}

    def register(self, cmd, callback=None, *, stdout=None, stderr=None, returncode=None):
        if not isinstance(cmd, str):
            raise ValueError('cmd must be a str')

        if callback is not None and not isinstance(callback, Exception) and not callable(callback):
            raise TypeError('callback should be an Exception or a callable')

        by_callback = callback
        by_output = (stdout, stderr, returncode)

        if by_callback is None and by_output == (None, None, None):
            raise ValueError('Meaningless behavior')

        if by_callback is not None and by_output != (None, None, None):
            raise ValueError('Ambiguous behavior')

        if cmd not in self.rules:
            self.rules[cmd] = []

        if by_callback:
            if isinstance(by_callback, Exception):
                behavior = by_callback
            else:
                def behavior(proc, *args):
                    proc.cmd = (cmd, *args)
                    return by_callback(proc, *args)

        else:
            def behavior(proc, *args):
                proc.cmd = (cmd, *args)
                if by_output[0]:
                    proc.stdout.writelines(by_output[0])
                if by_output[1]:
                    proc.stderr.writelines(by_output[1])
                return by_output[2]

        self.rules[cmd].append(behavior)
        return self

    def __call__(self, cmd, *,
                 stdin=None, stdout=True, stderr=True,
                 encoding='utf8', rstrip='\r\n',
                 bufsize=-1,
                 env=None,
                 wait=True):
        if not cmd:
            raise ValueError('command is empty')

        if isinstance(cmd, str):
            cmd = [cmd]

        matched_callbacks = None

        if cmd[0] in self.rules:
            matched_callbacks = self.rules[cmd[0]]
        elif '*' in self.rules:
            matched_callbacks = self.rules['*']
        else:
            raise ValueError('Unregistered command: {}'.format(cmd))

        behavior = matched_callbacks[0]
        if len(matched_callbacks) > 1:
            matched_callbacks.pop(0)

        if isinstance(behavior, Exception):
            raise behavior

        from .lib_subproc import command
        p = command([behavior] + cmd[1:],
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    encoding=encoding, rstrip=rstrip,
                    bufsize=bufsize,
                    env=env)
        p.run(wait=wait)
        return p


class FakeTerminalCell:
    def __init__(self, char, attr):
        self.char = char
        self.attr = attr

    @property
    def width(self):
        from .lib_tui import charwidth
        return charwidth(self.char)


class FakeTerminalCursor:
    def __init__(self):
        self.reset()

    def reset(self):
        self.y = 0
        self.x = 0
        self.attr = color()
        self.visible = True

    def __eq__(self, other):
        return (self.y, self.x) == other

    def __repr__(self): # pragma: no cover
        return 'Cursor(y={}, x={}, attr={}, visible={})'.format(
                self.y, self.x, repr(self.attr), self.visible)


@export
class FakeTerminal:
    def __init__(self, *, columns=80, lines=24):
        if columns < 0:
            raise ValueError('columns must >= 0')
        if lines < 0:
            raise ValueError('lines must >= 0')
        self.width = columns
        self.height = lines
        self.canvas = [[]]
        self.cursor = FakeTerminalCursor()

        self.chewing = ''

        self.recording_history = False

    @getter
    def recording(self):
        return self.recording_history

    @setter
    def recording(self, enable):
        if not isinstance(enable, bool):
            raise TypeError('recording must be a boolean')

        self.recording_history = [] if enable else False

    def __getitem__(self, idx):
        return ''.join(cell.char for cell in self.canvas[idx] if cell is not None).rstrip(' ')

    def __len__(self):
        return len(self.canvas)

    def __eq__(self, other):
        return self.lines == other

    @property
    def lines(self):
        return [self[idx] for idx in range(len(self))]

    def reset(self):
        self.canvas = [[]]
        self.cursor.reset()

    def get_terminal_size(self, *args, **kwargs):
        from os import terminal_size
        return terminal_size((
            self.width or max(len(line) for line in self),
            self.height or len(self.canvas)
            ))

    def ensure_cursor_pos(self):
        from .lib_math import clamp
        self.cursor.y = clamp(0, self.cursor.y, self.height or self.cursor.y)
        self.cursor.x = clamp(0, self.cursor.x, self.width or self.cursor.x)

        # Ensure canvas has enough lines
        while self.cursor.y >= len(self.canvas):
            self.canvas.append([])

    def print(self, *args, sep=' ', end='\n', **kwargs):
        if end is None:
            end = '\n'
        self.puts(sep.join(str(arg) for arg in args) + end)

    def puts(self, text):
        for char in text:
            self.chewing += char
            if self.check_control_seq():
                continue
            if self.chewing and self.chewing.isprintable():
                self.putc(self.chewing)
                self.chewing = ''

        if isinstance(self.recording_history, list):
            self.recording_history.append(text)

    def putc(self, char):
        cell = FakeTerminalCell(char, attr=self.cursor.attr)

        self.ensure_cursor_pos()

        # Make sure canvas is wide enough
        # Pre-fill spaces to make index-calculation easier
        for i in range(len(self.canvas[self.cursor.y]), self.cursor.x + cell.width):
            self.canvas[self.cursor.y].append(FakeTerminalCell(' ', attr=self.cursor.attr))

        current_line = self.canvas[self.cursor.y]
        current_char = self.canvas[self.cursor.y][self.cursor.x]

        if current_char is None:
            # Override the right-half of a wide-char on the left
            self.canvas[self.cursor.y][self.cursor.x - 1] = FakeTerminalCell(' ', attr=self.cursor.attr)

        # Override char under cursor
        self.canvas[self.cursor.y][self.cursor.x] = cell

        if cell.width == 2:
            # For wide-char, check if it overrides the next char
            next_char = self.canvas[self.cursor.y][self.cursor.x + 1]
            if next_char is not None and next_char.width == 2:
                self.canvas[self.cursor.y][self.cursor.x + 2] = FakeTerminalCell(' ', attr=self.cursor.attr)

            self.canvas[self.cursor.y][self.cursor.x + 1] = None

        # wrap
        if self.width and self.cursor.x >= self.width:
            self.cursor.y += 1
            self.cursor.x = 0

        self.cursor.x += cell.width

    def check_control_seq(self):
        m = rere(self.chewing)

        if self.chewing == '\033c':
            # Reset terminal to initial state
            self.reset()
            return True

        elif self.chewing == '\r':
            # Carriage return
            self.cursor.x = 0

        elif self.chewing == '\n':
            # Newline
            self.cursor.x = 0
            self.cursor.y += 1

        elif m.fullmatch('\033' + r'\[(\d*)([AB])'):
            # move cursor up/down
            direction = (1 if m.group(2) == 'B' else -1)
            self.cursor.y += int(m.group(1) or 1) * direction
            if direction == 1:
                self.cursor.y = min(self.cursor.y, len(self.canvas) - 1)

        elif m.fullmatch('\033' + r'\[(\d*)([CD])'):
            # move cursor right/left
            direction = (1 if m.group(2) == 'C' else -1)
            self.cursor.x += int(m.group(1) or 1) * direction

        elif self.chewing == '\033[H':
            self.cursor.y = 0
            self.cursor.x = 0

        elif m.fullmatch('\033' + r'\[(\d*);(\d*)H'):
            self.cursor.y = int(m.group(1) or 1) - 1
            self.cursor.x = int(m.group(2) or 1) - 1

        elif self.chewing == '\033[K':
            self.canvas[self.cursor.y] = self.canvas[self.cursor.y][:self.cursor.x]
            # Check is last character is cut into half
            if (self.cursor.x > 0 and
                self.canvas[self.cursor.y][-1] is not None and
                self.canvas[self.cursor.y][-1].width == 2):
                # if yes, replace it with a space
                self.canvas[self.cursor.y][-1] = FakeTerminalCell(' ', attr=color())

        elif m.fullmatch('\033' + r'\[([\d;]*)m'):
            self.cursor.attr = color(self.cursor.attr.seq + self.chewing)

        elif self.chewing == '\033[?25h':
            self.cursor.visible = True

        elif self.chewing == '\033[?25l':
            self.cursor.visible = False

        else:
            import string
            if (self.chewing and
                self.chewing.startswith('\033') and
                self.chewing[-1] in string.ascii_letters):
                # Escape sequence is terminated but it's unknown, drop it
                self.chewing = ''
            return False

        # Consume the escape sequence
        self.chewing = ''

        self.ensure_cursor_pos()

        return True


def main_thread():
    return threading.main_thread()


def current_thread():
    return threading.current_thread()


@export
class FakeTime:
    def __init__(self, *, testcase=None, base=0):
        assert testcase
        self.testcase = testcase
        self.world_time = base
        self.mailbox = queue.Queue()
        self.pin_list = []
        self.thread = None
        self.thread_status = {}

        me = self
        class FakeTimerWrapper(FakeTimer):
            def __init__(s, *args, **kwargs):
                super().__init__(me, *args, **kwargs)
        self.FakeTimerWrapper = FakeTimerWrapper

        class FakeThreadWrapper(FakeThread):
            def __init__(s, *args, **kwargs):
                super().__init__(me, *args, **kwargs)
        self.FakeThreadWrapper = FakeThreadWrapper

        class FakeEventWrapper(FakeEvent):
            def __init__(s, *args, **kwargs):
                super().__init__(me, *args, **kwargs)
        self.FakeEventWrapper = FakeEventWrapper

        self.patchers = []

        from collections import namedtuple
        self.Pin = namedtuple('Pin', ('timestamp', 'mailbox', 'msg'))

    def patch(self):
        patch_list = (
                ('time.time', self.time),
                ('time.monotonic', self.time),
                ('time.sleep', self.sleep),
                ('threading.Timer', self.FakeTimerWrapper),
                ('threading.Thread', self.FakeThreadWrapper),
                ('threading.Event', self.FakeEventWrapper),
                )

        for name, func in patch_list:
            self.patchers.append(self.testcase.patch(name, func))
        return self.patchers

    def unpatch(self):
        for patcher in self.patchers:
            patcher.stop()
        self.patchers = []

    def setup(self):
        self.patch()
        self.mail('start', current_thread())
        self.thread = Thread(target=self.event_loop)
        self.thread.daemon = True
        self.thread.start()

    def teardown(self):
        if not self.thread or not self.thread.is_alive():
            return

        self.mailbox.put(None)
        remaining_threads = list(self.thread_status.keys())
        for thread in remaining_threads:
            if thread is not main_thread() and not thread.daemon: # pragma: no cover 
                assert not thread.is_alive()
        self.thread.join()
        self.thread = None

    def mail(self, event, *args, **kwargs):
        self.mailbox.put((event, args, kwargs))

    def event_loop(self):
        while True:
            mail = self.mailbox.get()
            if not mail:
                break

            handler = getattr(self, 'handle_' + mail[0])
            handler(*mail[1], **mail[2])

            if self.mailbox.empty():
                self.schedule_next_task()

    def handle_start(self, thread):
        self.thread_status[thread] = True

    def handle_end(self, thread):
        self.thread_status.pop(thread, None)

    def handle_suspend(self, thread):
        self.thread_status[thread] = False

    def handle_resume(self, thread):
        self.thread_status[thread] = True

    def handle_pin(self, secs, mailbox, msg):
        self.pin_list.append(self.Pin(
            timestamp=self.world_time + secs,
            mailbox=mailbox, msg=msg))
        self.pin_list.sort(key=lambda x: x[0])

    def handle_unpin(self, mailbox):
        assert self.pin_list
        self.pin_list = [pin for pin in self.pin_list if pin.mailbox is not mailbox]

    def schedule_next_task(self):
        if not any(self.thread_status.values()):
            if self.pin_list:
                self.advance_to(self.pin_list[0].timestamp)

    def advance_to(self, timestamp):
        self.world_time = max(self.world_time, timestamp)

        expired_list = []
        waiting_list = []

        for pin in self.pin_list:
            (expired_list if pin[0] <= self.world_time else waiting_list).append(pin)

        self.pin_list = waiting_list

        barrier = threading.Barrier(len(expired_list) + 1)

        for pin in expired_list:
            pin.mailbox.put((barrier, pin.msg))

        barrier.wait()

    def time(self):
        if not self.thread:
            raise RuntimeError('Need to run in FakeTime context')
        return self.world_time

    def sleep(self, secs):
        if not self.thread:
            raise RuntimeError('Need to run in FakeTime context')

        if secs < 0:
            raise ValueError('This Python implementation is not powerful enough to rewind time')

        if secs == 0:
            return

        mailbox = queue.Queue()
        self.mail('pin', secs=secs, mailbox=mailbox, msg=None)
        self.mail('suspend', current_thread())
        barrier, msg = mailbox.get()
        self.mail('resume', current_thread())
        barrier.wait()


class FakeTimer:
    def __init__(self, world, interval, function, args=[], kwargs={}):
        self.world = world

        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs

        self.thread = threading.Thread(target=self.gogo, daemon=True)
        self.active = threading.Event()
        self.expired = threading.Event()
        self.finished = threading.Event()
        self.canceled = threading.Event()
        self.mailbox = queue.Queue()

    def gogo(self):
        self.active.set()
        import time
        self.world.mail('pin', secs=self.interval, mailbox=self.mailbox, msg='expired')
        self.world.mail('suspend', current_thread())
        barrier, msg = self.mailbox.get()
        self.world.mail('resume', current_thread())
        if not self.canceled.is_set():
            self.expired.set()
            self.function(*self.args, **self.kwargs)
            self.finished.set()
        barrier.wait()

    def start(self):
        self.expired.clear()
        self.canceled.clear()
        self.finished.clear()
        self.thread.start()
        self.active.wait()

    def cancel(self):
        self.world.mail('unpin', mailbox=self.mailbox)
        self.active.clear()
        self.canceled.set()
        self.finished.set()
        self.mailbox.put((threading.Barrier(1), 'canceled'))

    def join(self, timeout=None):
        if not self.active.is_set():
            return

        mailbox = queue.Queue()
        if timeout:
            self.world.mail('pin', secs=timeout, mailbox=mailbox, msg='timeout')
            self.world.mail('suspend', current_thread())
            barrier, msg = mailbox.get()
            barrier.wait()
            mailbox.task_done()
        else:
            self.world.mail('suspend', current_thread())
            self.finished.wait()

        self.world.mail('resume', current_thread())


class FakeThread:
    def __init__(self, world, target=None, *args, **kwargs):
        self.world = world

        self.target = target
        self.thread = Thread(target=self.gogo, *args, **kwargs)
        self.active = threading.Event()

    def __getattr__(self, name):
        return getattr(self.thread, name)

    def gogo(self, *args, **kwargs):
        self.active.set()
        self.world.mail('start', current_thread())
        if self.target:
            self.target(*args, **kwargs)
        self.world.mail('end', current_thread())

    def start(self, *args, **kwargs):
        self.thread.start(*args, **kwargs)
        self.active.wait()

    def join(self, timeout=None):
        if not self.thread.is_alive():
            self.thread.join(timeout=timeout)
            return

        mailbox = queue.Queue()
        if timeout:
            self.world.mail('pin', secs=timeout, mailbox=mailbox, msg='timeout')
            self.world.mail('suspend', current_thread())
            barrier, msg = mailbox.get()
            barrier.wait()
            mailbox.task_done()
        else:
            self.world.mail('suspend', current_thread())
            self.thread.join()

        self.world.mail('resume', current_thread())

    @getter
    def daemon(self):
        return self.thread.daemon

    @setter
    def daemon(self, value):
        self.thread.daemon = value


class FakeEvent:
    def __init__(self, world):
        self.world = world
        self.event = Event()

    def __getattr__(self, name):
        return getattr(self.event, name)

    def wait(self, timeout=None):
        import inspect
        frame = inspect.stack()[1]
        if frame.filename.endswith('/threading.py'):
            return self.event.wait(timeout=timeout)

        mailbox = queue.Queue()
        if timeout:
            self.world.mail('pin', secs=timeout, mailbox=mailbox, msg='timeout')
            self.world.mail('suspend', current_thread())
            barrier, msg = mailbox.get()
            barrier.wait()
            mailbox.task_done()
        else:
            self.world.mail('suspend', current_thread())
            self.event.wait()

        self.world.mail('resume', current_thread())
