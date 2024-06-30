import queue

from unittest.mock import patch

from .test_utils import *

from smol.subproc import *


def queue_to_list(Q):
    ret = []
    while not Q.empty():
        ret.append(Q.get())
    return ret


class TestStream(TestCase):
    def test_stream(self):
        s = stream()
        s.keep = True
        s.writeline('line1')
        s.writeline('line2')
        s.writeline('line3')
        self.is_false(s.closed)
        s.close()
        self.is_true(s.closed)
        self.eq(s.lines, ['line1', 'line2', 'line3'])

        s = stream()
        lines = ['line1', 'line2', 'line3']
        s.writelines(lines)
        s.close()
        self.eq(s.lines, [])
        for nr, line in enumerate(s):
            self.eq(lines[nr], line)
        self.eq(s.lines, [])

    def test_stream_nokeep(self):
        s = stream()
        # s.keep = False # Default
        s.writeline('line1')
        s.writeline('line2')
        s.writeline('line3')
        self.is_true(s.empty)


class TestSubproc(TestCase):
    def test_stdout(self):
        p = run('seq 5'.split())
        self.eq(p.stdout.lines, '1 2 3 4 5'.split())

    def test_run_and_then_wait(self):
        p = run('seq 5'.split(), wait=False)
        self.eq(p.stdout.lines, [])
        p.wait()
        self.eq(p.stdout.lines, '1 2 3 4 5'.split())

    def test_wait_early(self):
        p = command('seq 5'.split())
        p.wait()
        p.run(wait=False)
        p.wait()
        self.eq(p.stdout.lines, '1 2 3 4 5'.split())

    def test_context_manager_nowait(self):
        with command('seq 5'.split()) as p:
            self.eq(p.stdout.lines, [])
        self.eq(p.stdout.lines, '1 2 3 4 5'.split())

    def test_stdout_nokeep(self):
        p = command('seq 5'.split(), stdout=False)
        p.run()
        self.eq(p.stdout.lines, [])

    def test_keep_trailing_whitespaces(self):
        p = run(['echo', 'a b c '])
        self.eq(p.stdout.lines, ['a b c '])

    def test_callable(self):
        def prog(proc, *args):
            self.eq(args, ('arg1', 'arg2'))
            for idx, line in enumerate(proc[0]):
                proc[(idx % 2) + 1].writeline(line)
            return 2024

        p = run([prog, 'arg1', 'arg2'], stdin=['hello ', 'how are you ', 'im fine ', 'thank you '])
        self.eq(p.stdout.lines, ['hello ', 'im fine '])
        self.eq(p.stderr.lines, ['how are you ', 'thank you '])
        self.eq(p.returncode, 2024)

    def test_callback(self):
        lines = []
        def callback(line):
            lines.append(line)
        p = command('seq 5'.split(), stdout=callback)
        p.run()
        self.eq(lines, ['1', '2', '3', '4', '5'])

    def test_stdout_queue(self):
        Q = queue.Queue()
        p = command('seq 5'.split(), stdout=Q)
        self.is_false(p.stdout.keep)
        p.run()
        self.eq(p.stdout.lines, [])
        self.eq(queue_to_list(Q), ['1', '2', '3', '4', '5'])

    def test_multi_ouptut_merge(self):
        def prog(proc, *args):
            for i in range(5):
                proc[1].writeline(i)
                proc[2].writeline(i)

        Q = queue.Queue()

        lines = []
        def callback(line):
            lines.append(line)

        self.is_true(hasattr(Q, 'put'))

        p = command(prog, stdout=(Q, callback, True), stderr=(Q, True))
        p.run()
        self.eq(p.stdout.lines, [0, 1, 2, 3, 4])
        self.eq(p.stderr.lines, [0, 1, 2, 3, 4])
        self.eq(lines, [0, 1, 2, 3, 4])

        self.eq(queue_to_list(Q), [0, 0, 1, 1, 2, 2, 3, 3, 4, 4])

    def test_stdin(self):
        p = command('nl -w 1 -s :'.split(), stdin=['hello', 'world'])
        p.run(wait=False).wait()
        self.eq(p.stdout.lines, ['1:hello', '2:world'])

    def test_stdin_delayed_write(self):
        data = []
        p = command('nl -w 1 -s :'.split(), stdin=data)

        data += ['hello', 'world']
        data.append('hello')
        data.append('world')
        p.stdin.writeline('wah')
        p.run(wait=False).wait()

        self.eq(p.stdout.lines, ['1:wah', '2:hello', '3:world', '4:hello', '5:world'])

    def test_stdin_queue(self):
        Q = queue.Queue()
        p = command('nl -w 1 -s :'.split(), stdin=Q)

        p.run(wait=False)

        Q.put('hello')
        Q.put('world')
        Q.join()
        Q.put('wah')
        Q.join()

        p.stdin.close()

        p.wait()
        self.eq(p.stdout.lines, ['1:hello', '2:world', '3:wah'])

    def test_pipe(self):
        p1 = command('nl -w 1 -s :'.split(), stdin=['hello', 'world'])
        p2 = command('nl -w 1 -s /'.split(), stdin=True)
        pp = pipe(p1.stdout, p2.stdin)

        p1.run()
        self.eq(p1.stdout.lines, ['1:hello', '2:world'])
        p2.run(wait=False)

        p2.wait()
        self.eq(p2.stdin.lines, ['1:hello', '2:world'])
        self.eq(p2.stdout.lines, ['1/1:hello', '2/2:world'])

    def test_callable_with_pipe(self):
        def prog(proc, *args):
            for line in proc[0]:
                proc[1].writeline(line)
                proc[2].writeline(line)
            return 2024

        p1 = command(prog, stdin=['hello', 'world'])
        p2 = command('nl -w 1 -s :'.split(), stdin=True)
        p3 = command('nl -w 1 -s /'.split(), stdin=True)
        pipe(p1.stdout, p2.stdin)
        pipe(p1.stderr, p3.stdin)

        p1.run()
        p2.run()
        p3.run()

        self.eq(p1.returncode, 2024)
        self.eq(p2.stdout.lines, ['1:hello', '2:world'])
        self.eq(p3.stdout.lines, ['1/hello', '2/world'])

    def test_callable_raises_exception(self):
        def prog(proc, *args):
            # NameError
            n + 1

        with self.assertRaises(NameError):
            p = run(prog)

    def test_loopback(self):
        # Collatz function
        def collatz_function(x):
            return (x // 2) if (x % 2 == 0) else (3 * x + 1)

        def prog(proc, *args):
            for line in proc[0]:
                x = line
                if x == 1:
                    break
                else:
                    proc[1].writeline(collatz_function(x))

        p = command(prog, stdin=True)

        # loopback
        pipe(p.stdout, p.stdin)

        import time
        t = int(time.time())
        p.stdin.writeline(t)
        p.run()

        # If this test fails, make sure to check the initial input
        self.eq(p.stdout.lines[-1], 1, p.stdin.lines[0])

    def test_timeout(self):
        import time

        p = command(['sleep', 3])
        t1 = time.time()
        try:
            p.run(timeout=0.1)
        except TimeoutExpired:
            pass
        t2 = time.time()
        self.le(t2 - t1, 1)
        p.kill()

    def test_kill_callable(self):
        checkpoint = self.checkpoint()

        def prog(proc, *args):
            proc.killed.wait()
            checkpoint.set()

        p = run(prog, wait=False)
        p.kill()
        p.wait()
        checkpoint.is_set()

    def test_read_stdout_twice(self):
        ans = '1 2 3 4 5'.split()
        p = run('seq 5'.split())

        lines = []
        for line in p.stdout:
            lines.append(line)
        self.eq(lines, ans)

        checkpoint = self.checkpoint()
        lines = []
        def may_stuck():
            for line in p.stdout:
                lines.append(line)
            checkpoint.set()

        with self.run_in_thread(may_stuck):
            checkpoint.is_set()
            self.eq(lines, ans)


class TestSubprocRunMocker(TestCase):
    def test_mock_basic(self):
        mock = RunMocker()

        def mock_wah(proc, *args):
            proc.stdout.writeline('mock wah')
            if args:
                proc.stdout.writeline(' '.join(args))
            return 0
        mock.register('wah', mock_wah)

        # MOCK
        run = mock

        p = run('wah'.split())
        self.eq(p.stdout.lines, ['mock wah'])

        p = run('wah wah wah'.split())
        self.eq(p.stdout.lines, ['mock wah', 'wah wah'])

    def test_mock_unregistered_cmd(self):
        mock = RunMocker()

        mock.register('wah', lambda proc: 0)

        # MOCK
        run = mock

        run('wah'.split())

        with self.assertRaises(ValueError):
            p = run('ls -a -l'.split())

    def test_mock_side_effect(self):
        mock = RunMocker()

        def mock_ls_1st(proc, *args):
            self.eq(args, ('-a', '-l'))
            proc.stdout.writeline('file1')
        def mock_ls_2nd(proc, *args):
            self.eq(args, ('-a', '-l'))
            proc.stdout.writeline('file2')
        def mock_ls_3rd(proc, *args):
            self.eq(args, ('-a', '-l'))
            proc.stdout.writeline('file3')
        mock.register('ls', mock_ls_1st)
        mock.register('ls', mock_ls_2nd)
        mock.register('ls', mock_ls_3rd)

        # MOCK
        run = mock

        p = run('ls -a -l'.split())
        self.eq(p.returncode, None)
        self.eq(p.stdout.lines, ['file1'])

        p = run('ls -a -l'.split())
        self.eq(p.returncode, None)
        self.eq(p.stdout.lines, ['file2'])

        p = run('ls -a -l'.split())
        self.eq(p.returncode, None)
        self.eq(p.stdout.lines, ['file3'])

    def test_mock_pattern_matching(self):
        mock = RunMocker()

        def mock_ls0(proc):
            proc.stdout.writeline('mock ls0')
            return 0
        mock.register('ls', mock_ls0)

        def mock_ls1(proc, arg1):
            proc.stdout.writeline('mock ls1')
            proc.stdout.writeline(arg1)
            return 1
        mock.register(['ls', '{}'], mock_ls1)

        def mock_ls2(proc, arg1, arg2):
            proc.stdout.writeline('mock ls2')
            proc.stdout.writeline(arg1 + ' ' + arg2)
            return 2
        mock.register(['ls', '{}', '{}'], mock_ls2)

        def mock_ls22(proc, arg1, arg2):
            proc.stdout.writeline('mock ls22')
            proc.stdout.writeline(arg1 + ' ' + arg2)
            return 22
        mock.register(['ls', '{}', '-l', '{}'], mock_ls22)

        def mock_rm_r(proc, arg1):
            proc.stdout.writeline('mock rm')
            proc.stdout.writeline('-r' + ' ' + arg1)
            return 65530
        mock.register(['rm', '{}', '-r'], mock_rm_r)
        mock.register(['rm', '-r', '{}'], mock_rm_r)

        def mock_rm_f(proc, arg1):
            proc.stdout.writeline('mock rm')
            proc.stdout.writeline('-f' + ' ' + arg1)
            return 65535
        mock.register(['rm', '-f', '{}'], mock_rm_f)

        # MOCK
        run = mock

        p = run('ls'.split())
        self.eq(p.returncode, 0)
        self.eq(p.stdout.lines, ['mock ls0'])

        p = run('ls -a'.split())
        self.eq(p.returncode, 1)
        self.eq(p.stdout.lines, ['mock ls1', '-a'])

        p = run('ls -a -l'.split())
        self.eq(p.returncode, 2)
        self.eq(p.stdout.lines, ['mock ls2', '-a -l'])

        p = run('ls A -l B'.split())
        self.eq(p.returncode, 22)
        self.eq(p.stdout.lines, ['mock ls22', 'A B'])

        # I dont have balls to remove root dir
        p = run('rm -r non_exist'.split())
        self.eq(p.stdout.lines, ['mock rm', '-r non_exist'])
        self.eq(p.returncode, 65530)

        p = run('rm non_exist -r'.split())
        self.eq(p.stdout.lines, ['mock rm', '-r non_exist'])
        self.eq(p.returncode, 65530)

        p = run('rm -f non_exist'.split())
        self.eq(p.stdout.lines, ['mock rm', '-f non_exist'])
        self.eq(p.returncode, 65535)

        with self.assertRaises(ValueError):
            run('rm non_exist -f'.split())

    def test_mock_with_stdout_stderr_returncode(self):
        mock = RunMocker()
        mock.register('wah',
                      stdout=['wah', 'wah wah', 'wah wah wah'],
                      stderr=['WAH', 'WAH WAH', 'WAH WAH WAH'],
                      returncode=520)

        # MOCK
        run = mock

        p = run(['wah'])
        self.eq(p.stdout.lines, ['wah', 'wah wah', 'wah wah wah'])
        self.eq(p.stderr.lines, ['WAH', 'WAH WAH', 'WAH WAH WAH'])
        self.eq(p.returncode, 520)
