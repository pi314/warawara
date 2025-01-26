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

    def unset(self):
        self.checkpoint.clear()

    def wait(self):
        self.checkpoint.wait()

    def is_set(self):
        return self.checkpoint.is_set()

    def check(self):
        self.testcase.true(self.checkpoint.is_set(), 'Checkpoint was not set')

    def __bool__(self):
        return self.is_set()


@export
class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eq = self.assertEqual
        self.ne = self.assertNotEqual
        self.le = self.assertLessEqual
        self.true = self.assertTrue
        self.false = self.assertFalse

    def checkpoint(self):
        return Checkpoint(self)

    class run_in_thread:
        def __init__(self, func, args=tuple()):
            self.func = func
            self.args = args
            self.thread = threading.Thread(target=func, args=args)
            self.thread.daemon = True

        def __enter__(self, *args):
            self.thread.start()

        def __exit__(self, exc_type, exc_value, traceback):
            self.thread.join()

    def patch(self, name, side_effect):
        patcher = unittest.mock.patch(name, side_effect=side_effect)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing
