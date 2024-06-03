import queue

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

    def test_context_manager_run(self):
        with run('seq 5'.split()) as p:
            self.eq(p.stdout.lines, '1 2 3 4 5'.split())

    def test_context_manager_run_and_nowait(self):
        with run('seq 5'.split(), wait=False) as p:
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
            for idx, line in enumerate(proc[0]):
                proc[(idx % 2) + 1].writeline(line)
            return 2024

        p = run(prog, stdin=['hello ', 'how are you ', 'im fine ', 'thank you '])
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
        pipe(p1.stdout, p2.stdin)

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
        checkpoint = False
        def prog(proc, *args):
            nonlocal checkpoint
            proc.killed.wait()
            checkpoint = True

        p = run(prog, wait=False)
        p.kill()
        p.wait()
        self.is_true(checkpoint)
