from .test_utils import *

from smol.itertools import *


class TestItertools(TestCase):
    def test_iter(self):
        data = []
        for val, is_last in lookahead([1, 2, 3, 4, 5]):
            data.append((val, is_last))

        self.eq(data, [
            (1, False),
            (2, False),
            (3, False),
            (4, False),
            (5, True),
            ])
