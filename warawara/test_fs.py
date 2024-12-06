from .test_utils import *

import warawara as wrwr


class TestFs(TestCase):
    def test_fsorted(self):
        self.eq(wrwr.fsorted([
            'apple1',
            'apple10',
            'banana10',
            'apple2',
            'banana1',
            'banana3',
            ]), [
                'apple1',
                'apple2',
                'apple10',
                'banana1',
                'banana3',
                'banana10',
                ])

        self.eq(wrwr.fsorted([
            'version-1.9',
            'version-2.0',
            'version-1.11',
            'version-1.10',
            ]), [
            'version-1.9',
            'version-1.10',
            'version-1.11',
            'version-2.0',
            ])
