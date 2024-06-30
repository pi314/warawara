import unittest
import threading


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
        self.testcase.is_true(self.checkpoint.is_set(), 'Checkpoint was not set')


class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eq = self.assertEqual
        self.ne = self.assertNotEqual
        self.le = self.assertLessEqual
        self.is_true = self.assertTrue
        self.is_false = self.assertFalse

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
