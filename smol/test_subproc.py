import queue

from .test_utils import *

from smol.subproc import *


def queue_to_list(Q):
    ret = []
    while not Q.empty():
        ret.append(Q.get())
    return ret


class TestSubproc(TestCase):
    def test_stream(self):
        s = stream()
        s.writeline('line1')
        s.writeline('line2')
        s.writeline('line3')
        self.eq(s.closed, False)
        s.close()
        self.eq(s.closed, True)
        self.eq(s.lines, ['line1', 'line2', 'line3'])

        s = stream()
        lines = ['line1', 'line2', 'line3']
        s.writelines(lines)
        s.close()
        for nr, line in enumerate(s):
            self.eq(lines[nr], line)

    def test_stdout(self):
        p = command('seq 5'.split())
        p.run(wait=False).wait()
        self.eq(p.stdout.lines, ['1', '2', '3', '4', '5'])

    def test_callback(self):
        lines = []
        def callback(line):
            lines.append(line)
        p = command('seq 5'.split(), stdout=callback)
        p.run()
        self.eq(p.stdout.lines, ['1', '2', '3', '4', '5'])
        self.eq(p.stdout.lines, lines)

    def test_stdout_queue(self):
        q = queue.Queue()

        p = command('seq 5'.split(), stdout=q)
        p.run()
        self.eq(p.stdout.lines, ['1', '2', '3', '4', '5'])
        self.eq(p.stdout.lines, queue_to_list(q))

    def test_multi_ouptut_merge(self):
        def proc(streams, *args):
            for i in range(5):
                streams[1].writeline(i)
                streams[2].writeline(i)

        Q = queue.Queue()

        lines = []
        def callback(line):
            lines.append(line)

        p = command(proc, stdout=(Q, callback), stderr=(Q))
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
        self.eq(p2.stdin.lines, ['1:hello', '2:world'])
        p2.run(wait=False)

        p2.wait()
        self.eq(p2.stdout.lines, ['1/1:hello', '2/2:world'])

    def test_callable_with_pipe(self):
        def proc(streams, *args):
            for line in streams[0]:
                streams[1].writeline(line)
                streams[2].writeline(line)
            return 2024

        p1 = command(proc, stdin=['hello', 'world'])
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

    def test_loopback(self):
        def three_n_plus_1(streams, *args):
            for line in streams[0]:
                n = line
                if n == 1:
                    break
                elif n % 2 == 0:
                    streams[1].writeline(n // 2)
                else:
                    streams[1].writeline(3 * n + 1)

        p = command(three_n_plus_1, stdin=True)

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
