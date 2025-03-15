import unittest
import threading


from .internal_utils import exporter
export, __all__ = exporter()


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

    def check(self, is_set=True):
        self.testcase.eq(
                self.checkpoint.is_set(),
                is_set,
                'Checkpoint was' + (' ' if self.checkpoint.is_set() else ' not ') + 'set')

    def __bool__(self):
        return self.is_set()


@export
class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eq = self.assertEqual
        self.ne = self.assertNotEqual
        self.le = self.assertLessEqual
        self.lt = self.assertLess
        self.ge = self.assertGreaterEqual
        self.gt = self.assertGreater
        self.true = self.assertTrue
        self.false = self.assertFalse
        self.raises = self.assertRaises

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
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing


@export
class RunMocker:
    def __init__(self):
        self.rules = {}

    def register(self, cmd, callback=None, *, stdout=None, stderr=None, returncode=None):
        if all((callback is None, stdout is None, stderr is None, returncode is None)):
            raise ValueError('Meaningless mock')

        if callback is not None and any((
                stdout is not None,
                stderr is not None,
                returncode is not None
                )):
            raise ValueError('Ambiguous mock')

        if not isinstance(cmd, str):
            cmd = tuple(cmd)

        if cmd not in self.rules:
            self.rules[cmd] = []

        if stdout is not None or stderr is not None or returncode is not None:
            def simple_prog(proc, *args):
                if stdout:
                    proc.stdout.writelines(stdout)
                if stderr:
                    proc.stderr.writelines(stderr)
                return returncode

            callback = simple_prog

        self.rules[cmd].append(callback)
        return self

    @classmethod
    def match_pattern(cls, pattern, cmd):
        if len(pattern) != len(cmd):
            return None

        args = []
        for parg, carg in zip(pattern, cmd):
            if parg == carg:
                pass
            elif parg == '{}':
                args.append(carg)
            else:
                return None

        return args

    def __call__(self, cmd, *,
                 stdin=None, stdout=True, stderr=True,
                 encoding='utf8', rstrip='\r\n',
                 bufsize=-1,
                 env=None,
                 wait=True):
        from .lib_subproc import command
        matched_pattern = None
        matched_args = []
        for rule in self.rules.items():
            pattern = rule[0]
            callbacks = rule[1]

            if isinstance(pattern, str):
                continue

            args = type(self).match_pattern(pattern, cmd)
            if args:
                matched_pattern = pattern
                matched_args = args

        if not matched_pattern:
            if cmd[0] in self.rules:
                matched_pattern = cmd[0]
                matched_args = cmd[1:]

        if not matched_pattern:
            raise ValueError('Unregistered command: {}'.format(cmd))

        matched_callbacks = self.rules[matched_pattern]

        callback = matched_callbacks[0]
        if len(matched_callbacks) > 1:
            matched_callbacks.pop(0)

        p = command([callback] + matched_args,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    encoding=encoding, rstrip=rstrip,
                    bufsize=bufsize,
                    env=env)
        p.run(wait=wait)
        return p
