import threading

from .lib_test_utils import *

import warawara as wara


class TestCheckPoint(TestCase):
    def test_checkpoint(self):
        Checkpoint = wara.Checkpoint

        checkpoint = Checkpoint(self)

        self.false(checkpoint)
        checkpoint.set()
        checkpoint.check()

        checkpoint.unset()
        self.false(checkpoint)

        def set_checkpoint():
            checkpoint.wait()

        t = threading.Thread(target=set_checkpoint)
        t.daemon = True
        t.start()

        checkpoint.set()
        t.join()
