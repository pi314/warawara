import os
import shutil

from os.path import exists, isdir

from .test_utils import *

import warawara as wrwr


class TestSh(TestCase):
    def setUp(self):
        if exists('tmp') and isdir('tmp'):
            shutil.rmtree('tmp')

        os.mkdir('tmp')
        os.mkdir('tmp/a')
        os.mkdir('tmp/a/b')

    def tearDown(self):
        shutil.rmtree('tmp')

    def test_pushd_popd_dirs(self):
        cwd1 = wrwr.cwd()

        with wrwr.pushd('tmp'):
            self.eq(wrwr.cwd(), cwd1 / 'tmp')

            wrwr.pushd('a')
            self.eq(wrwr.cwd(), cwd1 / 'tmp/a')
            self.eq(wrwr.dirs(),
                    [
                        cwd1,
                        cwd1 / 'tmp',
                        cwd1 / 'tmp' / 'a',
                    ])

            wrwr.cwd(cwd1 / 'tmp' / 'a' / 'b')
            self.eq(wrwr.cwd(), cwd1 / 'tmp' / 'a' / 'b')
            wrwr.popd()

            self.eq(wrwr.cwd(), cwd1 / 'tmp')
            self.eq(wrwr.dirs(),
                    [
                        cwd1,
                        cwd1 / 'tmp',
                    ])

        self.eq(wrwr.cwd(), cwd1)
        self.eq(wrwr.dirs(),
                [
                    cwd1,
                ])

        wrwr.popd()
