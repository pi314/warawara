import os
import shutil

from .test_utils import *

import warawara as wrwr


class TestSh(TestCase):
    def setUp(self):
        shutil.rmtree('tmp')
        os.mkdir('tmp')
        os.mkdir('tmp/a')
        os.mkdir('tmp/a/b')

    def tearDown(self):
        shutil.rmtree('tmp')

    def test_sh(self):
        cwd1 = wrwr.cwd()

        wrwr.pushd('tmp')
        wrwr.pushd('a')
        self.eq(wrwr.cwd(), cwd1 / 'tmp/a')
        self.eq(wrwr.dirs(),
                [
                    cwd1,
                    cwd1 / 'tmp',
                    cwd1 / 'tmp' / 'a',
                ])

        wrwr.popd()
        self.eq(wrwr.dirs(),
                [
                    cwd1,
                    cwd1 / 'tmp',
                ])

        wrwr.popd()
        self.eq(wrwr.cwd(), cwd1)
        self.eq(wrwr.dirs(),
                [
                    cwd1,
                ])
