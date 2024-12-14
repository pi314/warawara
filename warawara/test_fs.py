import unittest.mock

from .test_utils import *

import warawara as wrwr


class TestFs(TestCase):
    def test_open(self):
        mock_open = unittest.mock.mock_open()
        self.patch('builtins.open', mock_open)

        with wrwr.open('warawara.txt', 'w') as f:
            f.write('normal write\n')
            f.writeline()
            f.writeline('line1')
            f.writelines(['line2', 'line3', 'line4'])

        mock_open.assert_called_once_with(
                'warawara.txt', 'w',
                encoding='utf-8', errors='backslashreplace')
        handle = mock_open()
        handle.write.assert_has_calls([
            unittest.mock.call('normal write\n'),
            unittest.mock.call('\n'),
            unittest.mock.call('line1\n'),
            unittest.mock.call('line2\n'),
            unittest.mock.call('line3\n'),
            unittest.mock.call('line4\n'),
            ])

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
