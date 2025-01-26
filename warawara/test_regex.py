from .lib_test_utils import *

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

        rec.search(r'\bwa\b')
        self.eq(rec.start(), 5)
        self.eq(rec.end(), 7)

        self.ne(rec.fullmatch(r'(\w+) (\w+) (\w+)'), None)

        self.eq(rec.split(' +'), rec.text.split(' '))

        self.eq(rec.findall(r'\b\w+\b'), ['wara', 'wa', 'ra'])

        self.eq(rec.subn(r'wa', 'WA'), ('WAra WA ra', 2))
