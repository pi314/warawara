import threading

from .lib_test_utils import *

import warawara as wara


class TestCheckPoint(TestCase):
    def test_checkpoint(self):
        Checkpoint = wara.Checkpoint

        checkpoint = Checkpoint(self)

        self.false(checkpoint)
        checkpoint.set()
        checkpoint.check()

        checkpoint.unset()
        self.false(checkpoint)

        def set_checkpoint():
            checkpoint.wait()

        t = threading.Thread(target=set_checkpoint)
        t.daemon = True
        t.start()

        checkpoint.set()
        t.join()


class TestSubprocRunMocker(TestCase):
    def test_mock_basic(self):
        mock_run = RunMocker()

        def mock_wah(proc, *args):
            proc.stdout.writeline('mock wah')
            if args:
                proc.stdout.writeline(' '.join(args))
            return 0
        mock_run.register('wah', mock_wah)

        p = mock_run('wah'.split())
        self.eq(p.stdout.lines, ['mock wah'])

        p = mock_run('wah wah wah'.split())
        self.eq(p.stdout.lines, ['mock wah', 'wah wah'])

    def test_mock_meaningless_mock(self):
        mock_run = RunMocker()

        with self.assertRaises(ValueError):
            mock_run.register('cmd')

    def test_mock_ambiguous_mock(self):
        mock_run = RunMocker()

        with self.assertRaises(ValueError):
            mock_run.register('wah', lambda: None, stdout='wah')

    def test_mock_unregistered_cmd(self):
        mock_run = RunMocker()

        mock_run.register('wah', lambda proc: 0)

        mock_run('wah'.split())

        with self.assertRaises(ValueError):
            p = mock_run('ls -a -l'.split())

    def test_mock_side_effect(self):
        mock_run = RunMocker()

        def mock_ls_1st(proc, *args):
            self.eq(args, ('-a', '-l'))
            proc.stdout.writeline('file1')
        def mock_ls_2nd(proc, *args):
            self.eq(args, ('-a', '-l'))
            proc.stdout.writeline('file2')
        def mock_ls_3rd(proc, *args):
            self.eq(args, ('-a', '-l'))
            proc.stdout.writeline('file3')
        mock_run.register('ls', mock_ls_1st)
        mock_run.register('ls', mock_ls_2nd)
        mock_run.register('ls', mock_ls_3rd)

        p = mock_run('ls -a -l'.split())
        self.eq(p.returncode, None)
        self.eq(p.stdout.lines, ['file1'])

        p = mock_run('ls -a -l'.split())
        self.eq(p.returncode, None)
        self.eq(p.stdout.lines, ['file2'])

        p = mock_run('ls -a -l'.split())
        self.eq(p.returncode, None)
        self.eq(p.stdout.lines, ['file3'])

    def test_mock_pattern_matching(self):
        mock_run = RunMocker()

        def mock_ls0(proc):
            proc.stdout.writeline('mock ls0')
            return 0
        mock_run.register('ls', mock_ls0)

        def mock_ls1(proc, arg1):
            proc.stdout.writeline('mock ls1')
            proc.stdout.writeline(arg1)
            return 1
        mock_run.register(['ls', '{}'], mock_ls1)

        def mock_ls2(proc, arg1, arg2):
            proc.stdout.writeline('mock ls2')
            proc.stdout.writeline(arg1 + ' ' + arg2)
            return 2
        mock_run.register(['ls', '{}', '{}'], mock_ls2)

        def mock_ls22(proc, arg1, arg2):
            proc.stdout.writeline('mock ls22')
            proc.stdout.writeline(arg1 + ' ' + arg2)
            return 22
        mock_run.register(['ls', '{}', '-l', '{}'], mock_ls22)

        def mock_rm_r(proc, arg1):
            proc.stdout.writeline('mock rm')
            proc.stdout.writeline('-r' + ' ' + arg1)
            return 65530
        mock_run.register(['rm', '{}', '-r'], mock_rm_r)
        mock_run.register(['rm', '-r', '{}'], mock_rm_r)

        def mock_rm_f(proc, arg1):
            proc.stdout.writeline('mock rm')
            proc.stdout.writeline('-f' + ' ' + arg1)
            return 65535
        mock_run.register(['rm', '-f', '{}'], mock_rm_f)

        p = mock_run('ls'.split())
        self.eq(p.returncode, 0)
        self.eq(p.stdout.lines, ['mock ls0'])

        p = mock_run('ls -a'.split())
        self.eq(p.returncode, 1)
        self.eq(p.stdout.lines, ['mock ls1', '-a'])

        p = mock_run('ls -a -l'.split())
        self.eq(p.returncode, 2)
        self.eq(p.stdout.lines, ['mock ls2', '-a -l'])

        p = mock_run('ls A -l B'.split())
        self.eq(p.returncode, 22)
        self.eq(p.stdout.lines, ['mock ls22', 'A B'])

        p = mock_run('rm -r non_exist'.split())
        self.eq(p.stdout.lines, ['mock rm', '-r non_exist'])
        self.eq(p.returncode, 65530)

        p = mock_run('rm non_exist -r'.split())
        self.eq(p.stdout.lines, ['mock rm', '-r non_exist'])
        self.eq(p.returncode, 65530)

        p = mock_run('rm -f non_exist'.split())
        self.eq(p.stdout.lines, ['mock rm', '-f non_exist'])
        self.eq(p.returncode, 65535)

        with self.assertRaises(ValueError):
            mock_run('rm non_exist -f'.split())

    def test_mock_with_returncode(self):
        mock_run = RunMocker()
        mock_run.register('wah', returncode=1)
        p = mock_run(['wah'])
        self.eq(p.returncode, 1)

    def test_mock_with_stdout_stderr_returncode(self):
        mock_run = RunMocker()
        mock_run.register('wah',
                      stdout=['wah', 'wah wah', 'wah wah wah'],
                      stderr=['WAH', 'WAH WAH', 'WAH WAH WAH'],
                      returncode=520)

        p = mock_run(['wah'])
        self.eq(p.stdout.lines, ['wah', 'wah wah', 'wah wah wah'])
        self.eq(p.stderr.lines, ['WAH', 'WAH WAH', 'WAH WAH WAH'])
        self.eq(p.returncode, 520)
