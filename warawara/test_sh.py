import os
import shutil

from pathlib import Path

from .test_utils import *

import warawara as wara


class TestSh(TestCase):
    def setUp(self):
        self.cwd = Path.cwd()
        self.patch('os.chdir', self.mock_chdir)
        self.patch('os.getcwd', self.mock_getcwd)

    def mock_getcwd(self):
        return str(self.cwd)

    def mock_chdir(self, path):
        path = Path(path)
        if path.is_absolute():
            self.cwd = path
        else:
            self.cwd = self.cwd / path

    def test_pushd_popd_dirs(self):
        cwd1 = wara.cwd()

        with wara.pushd('tmp'):
            self.eq(wara.cwd(), cwd1 / 'tmp')

            wara.pushd('a')
            self.eq(wara.cwd(), cwd1 / 'tmp/a')
            self.eq(wara.dirs(),
                    [
                        cwd1,
                        cwd1 / 'tmp',
                        cwd1 / 'tmp' / 'a',
                    ])

            wara.cwd(cwd1 / 'tmp' / 'a' / 'b')
            self.eq(wara.cwd(), cwd1 / 'tmp' / 'a' / 'b')
            wara.popd()

            self.eq(wara.cwd(), cwd1 / 'tmp')
            self.eq(wara.dirs(),
                    [
                        cwd1,
                        cwd1 / 'tmp',
                    ])

        self.eq(wara.cwd(), cwd1)
        self.eq(wara.dirs(),
                [
                    cwd1,
                ])

        wara.popd()

    def test_shrinkuser(self):
        HOME = wara.home()
        self.eq(wara.shrinkuser(HOME), '~')
        self.eq(wara.shrinkuser(str(HOME) + '/'), '~/')

        self.eq(wara.shrinkuser(HOME / 'bana'), '~/bana')
        self.eq(wara.shrinkuser(HOME / 'bana/'), '~/bana')
        self.eq(wara.shrinkuser(str(HOME) + '/bana/'), '~/bana/')

        self.eq(wara.shrinkuser('bana/na/'), 'bana/na/')
        self.eq(wara.shrinkuser('bana/na'), 'bana/na')
