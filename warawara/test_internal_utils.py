from .lib_test_utils import *

from .internal_utils import exporter


class TestInternalUtils(TestCase):
    def test_exporter(self):
        export, uualluu = exporter()

        self.eq(uualluu, [])

        export('wara')
        self.eq(uualluu, ['wara'])

        @export
        def test_func():
            pass

        self.eq(uualluu, ['wara', 'test_func'])

        export()
        self.eq(uualluu, ['wara', 'test_func'])
