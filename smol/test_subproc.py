import queue

from .test_utils import *

from smol.subproc import *


def queue_to_list(Q):
    ret = []
    while not Q.empty():
        ret.append(Q.get())
    return ret


class TestEventBroadcaster(TestCase):
    def test_all(self):
        data1 = []
        def handler1(arg):
            data1.append(arg)

        data2 = []
        def handler2(arg):
            data2.append(arg)

        import smol
        hub = smol.subproc.EventBroadcaster()
        hub.broadcast('...')

        hub += handler1
        hub.broadcast('wah')

        hub += handler2
        hub.broadcast('Wah')

        hub += handler2
        hub.broadcast('WAAAAAH')

        hub -= handler1
        hub.broadcast('wah?')

        hub -= handler2
        hub.broadcast('wow')

        hub -= handler2
        hub.broadcast('bye')

        self.eq(data1, ['wah', 'Wah', 'WAAAAAH'])
        self.eq(data2, ['Wah', 'WAAAAAH', 'WAAAAAH', 'wah?', 'wah?', 'wow'])


class TestStream(TestCase):
    def test_stream_basic_io(self):
        s = stream()
        self.eq(s.keep, False)

        s.writeline('line1')
        s.writeline('line2')
        s.writeline('line3')
        self.is_false(s.closed)

        s.close()
        self.is_true(s.closed)

        self.eq(s.lines, [])
        self.eq(s.readline(), 'line1')
        self.eq(s.readline(), 'line2')
        self.eq(s.readline(), 'line3')

    def test_stream_iter(self):
        s = stream()
        self.eq(s.keep, False)
        s.writelines(['line1', 'line2', 'line3'])

        i = iter(s)
        self.eq(next(i), 'line1')
        self.eq(next(i), 'line2')
        self.eq(next(i), 'line3')

        s.close()

        with self.assertRaises(StopIteration):
            next(iter(s))

    def test_stream_keep(self):
        s = stream()
        s.keep = True

        lines = ['line1', 'line2', 'line3']
        for line in lines:
            s.writeline(line)

        self.eq(s.lines, lines)
        self.eq(len(s), 3)

        self.is_false(s.empty)
        self.is_true(bool(s))

        self.eq(s.readline(), 'line1')
        self.eq(s.readline(), 'line2')
        self.eq(s.readline(), 'line3')

        self.eq(s.lines, lines)
        self.eq(len(s), 3)

    def test_stream_subscribers(self):
        data1 = []
        def handler1(line):
            data1.append(line)

        data2 = []
        def handler2(line):
            data2.append(line)

        Q = queue.Queue()

        s = stream()
        s.welcome([handler1, handler2])
        s.welcome(Q)
        s.welcome(True)

        with self.assertRaises(TypeError):
            s.welcome(s)

        lines = ['line1', 'line2', 'line3']
        s.writelines(lines)

        self.eq(data1, lines)
        self.eq(data2, lines)

    def test_stream_write_after_close(self):
        def should_not_be_called_handler(line):
            self.fail()

        # test in test
        with self.assertRaises(AssertionError):
            should_not_be_called_handler('wah')

        s = stream()
        s.welcome(should_not_be_called_handler)
        s.close()

        s.writeline('line1')

        with self.assertRaises(BrokenPipeError):
            s.writeline('line2', suppress=False)


class TestSubproc(TestCase):
    def test_default_properties(self):
        def prog(proc):
            self.eq(proc[0].readline(), 'line')

        p = run(prog, stdin='line', stdout=False, stderr=False)

    def test_stdout(self):
        p = run('seq 5'.split())
        self.eq(p.stdout.lines, '1 2 3 4 5'.split())

    def test_disable_stdout_and_stderr(self):
        p = command('seq 5'.split(), stdout=None, stderr=None)
        self.is_true(p.stdout.closed)
        self.is_true(p.stderr.closed)

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

    def test_already_running_error(self):
        checkpoint = self.checkpoint()

        def prog(proc, *args):
            checkpoint.wait()

        p = command(prog)
        p.run(wait=False)

        with self.assertRaises(AlreadyRunningError):
            p.run()

        checkpoint.set()
        p.wait()

        p = command(['sleep', 1])
        p.run(wait=False)
        with self.assertRaises(AlreadyRunningError):
            p.run(wait=False)
        p.kill()

    def test_word(self):
        p = run('true')
        self.eq(p.returncode, 0)

        p = run('false')
        self.eq(p.returncode, 1)

    def test_empty_cmd(self):
        with self.assertRaises(ValueError):
            p = command()

        with self.assertRaises(ValueError):
            p = command([])

    def test_run_with_context_manager(self):
        barrier = threading.Barrier(2)

        def prog(proc, *args):
            barrier.wait()

        with command(prog) as p:
            barrier.wait()

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

    def test_stdout_callback(self):
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
        p.run()
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

    def test_pipe_istream_already_closed(self):
        i = stream()
        o = stream()
        i.close()

        with self.assertRaises(EOFError):
            pipe(i, o)

    def test_pipe_ostream_already_closed(self):
        i = stream()
        o = stream()
        o.close()

        with self.assertRaises(BrokenPipeError):
            pipe(i, o)

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

        # I dont have balls to remove root dir
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
