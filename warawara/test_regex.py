from .test_utils import *

from warawara import *


class TestRegex(TestCase):
    def test_match(self):
        rec = rere('wara wa ra')

        m = rec.match(r'^(\w+) (\w+)$')
        self.eq(m, None)

        m = rec.match(r'^(\w+) (\w+) (\w+)$')
        self.eq(m.groups(), ('wara', 'wa', 'ra'))
        self.eq(m.group(2), 'wa')

        self.eq(rec.groups(), m.groups())
        self.eq(rec.group(2), m.group(2))

        self.eq(rec.sub(r'wara', 'WARA'), 'WARA wa ra')
