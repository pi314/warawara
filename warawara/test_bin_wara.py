import sys

import unittest.mock

from .lib_test_utils import *

import warawara as wara


class TestBinWara(TestCase):
    def setUp(self):
        self.prints = []
        self.patch('builtins.print', self.mock_print)

    def tearDown(self):
        pass

    def mock_print(self, *args, **kwargs):
        self.prints.append((args, kwargs))

    @property
    def stdout(self):
        return [' '.join(args)
                for args, kwargs in self.prints
                if kwargs.get('file', sys.stdout) == sys.stdout]

    @property
    def stderr(self):
        return [' '.join(args)
                for args, kwargs in self.prints
                if kwargs.get('file') == sys.stderr]

    def test_bin_wara(self):
        # Run 'warawara' and check output
        with self.raises(SystemExit):
            sys.argv = ['warawara']
            wara.bin.wara.main()

        modules = self.stdout

        import os
        import re
        files = list(
                map(
                    lambda x: re.fullmatch(r'bin_(\w+).py', x).group(1),
                    filter(lambda x: x.startswith('bin') and x.endswith('.py'),
                           os.listdir('warawara'))
                    )
                )
        self.eq(sorted(modules), sorted(files))

    def test_bin_wara_subcmd_rainbow(self):
        with self.raises(SystemExit):
            sys.argv = ['warawara', 'rainbow']
            wara.bin.wara.main()

        sys.argv = ['warawara', 'rainbow', 'murasaki']
        wara.bin.wara.main()

    def test_bin_wara_subcmd_unknown(self):
        with self.raises(SystemExit):
            sys.argv = ['warawara', 'wow']
            wara.bin.wara.main()

        self.true('Unknown' in '\n'.join(self.stderr))

    def test_bin_wara_recursion_error(self):
        with self.raises(SystemExit):
            sys.argv = ['warawara', 'wara', 'wara', 'wara']
            wara.bin.wara.main()

        self.true('RecursionError' in '\n'.join(self.stderr))
