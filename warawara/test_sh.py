import os
import shutil

from pathlib import Path

from .lib_test_utils import *

import warawara as wara


class TestSh(TestCase):
    def setUp(self):
        self.root = Path(__file__).parent
        self.cwd = self.root
        wara.sh.dir_stack = []
        self.patch('os.chdir', self.mock_chdir)
        self.patch('os.getcwd', self.mock_getcwd)

    def mock_getcwd(self):
        if isinstance(self.cwd, Exception):
            raise self.cwd

        if self.cwd == 'invalid':
            raise FileNotFoundError('invalid')

        return str(self.cwd)

    def mock_chdir(self, path):
        if path == 'invalid':
            raise FileNotFoundError('invalid')

        path = Path(path)
        if path.is_absolute():
            self.cwd = path
        else:
            self.cwd = self.cwd / path

    def test_cwd(self):
        self.eq(wara.cwd(), Path.cwd())
        self.eq(wara.cwd('tmp'), self.root / 'tmp')
        self.eq(wara.cwd('invalid'), False)
        self.eq(wara.cwd(0), False)
        self.eq(wara.cwd(True), False)

    def test_pushd_invalid_path(self):
        here = wara.cwd()

        p = wara.pushd('invalid')
        self.false(p)

        p = wara.pushd(3)
        self.false(p)

        self.eq(wara.cwd(), here)

    def test_pushd_invalid_cwd(self):
        self.cwd = FileNotFoundError('deleted')

        self.eq(wara.cwd(), False)

        p = wara.pushd('tmp')
        self.false(p)

    def test_popd_to_invalid_path(self):
        here = wara.cwd()

        wara.pushd('tmp')

        def mock_chdir(path):
            raise FileNotFoundError('deleted')
        self.patch('os.chdir', mock_chdir)

        self.false(wara.popd())

        self.eq(wara.cwd(), here / 'tmp')

    def test_dirs_clear(self):
        here = wara.cwd()
        wara.pushd('tmp')
        wara.pushd('tmp2')

        self.eq(wara.dirs(), [here, here / 'tmp', here / 'tmp' / 'tmp2'])

        wara.dirs(clear=True)

        self.eq(wara.dirs(), [here / 'tmp' / 'tmp2'])

    def test_popd_all(self):
        here = wara.cwd()
        wara.pushd('tmp')
        wara.pushd('tmp2')

        self.eq(wara.dirs(), [here, here / 'tmp', here / 'tmp' / 'tmp2'])

        wara.popd(all=True)

        self.eq(wara.dirs(), [here])

    def test_pushd_popd_dirs(self):
        here = wara.cwd()

        with wara.pushd('tmp'):
            self.eq(wara.cwd(), here / 'tmp')

            wara.pushd('a')
            self.eq(wara.cwd(), here / 'tmp' / 'a')
            self.eq(wara.dirs(),
                    [
                        here,
                        here / 'tmp',
                        here / 'tmp' / 'a',
                    ])

            wara.cwd(here / 'tmp' / 'b')
            self.eq(wara.cwd(), here / 'tmp' / 'b')

            self.eq(wara.popd(), True)

            self.eq(wara.cwd(), here / 'tmp')
            self.eq(wara.dirs(),
                    [
                        here,
                        here / 'tmp',
                    ])

        self.eq(wara.cwd(), here)
        self.eq(wara.dirs(), [here])

        self.eq(wara.popd(), False)

    def test_home(self):
        from os.path import expanduser
        self.eq(str(wara.home()), expanduser('~'))

    def test_shrinkuser(self):
        HOME = wara.home()
        self.eq(wara.shrinkuser(HOME), '~')
        self.eq(wara.shrinkuser(str(HOME) + '/'), '~/')

        self.eq(wara.shrinkuser(HOME / 'bana'), '~/bana')
        self.eq(wara.shrinkuser(HOME / 'bana/'), '~/bana')
        self.eq(wara.shrinkuser(str(HOME) + '/bana/'), '~/bana/')

        self.eq(wara.shrinkuser('bana/na/'), 'bana/na/')
        self.eq(wara.shrinkuser('bana/na'), 'bana/na')
