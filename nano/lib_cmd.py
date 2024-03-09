import queue
import subprocess as sub
import threading


class Stream:
    def __init__(self):
        self.Q = queue.Queue()
        self.__lines = []
        self.callbacks = []
        self.eof = threading.Event()

    def callback(self, callback):
        self.callbacks.append(callback)

    @property
    def lines(self):
        return self.__lines

    def readline(self):
        line = self.Q.get()
        for callback in self.callbacks:
            callback(line)
        return line

    def writeline(self, line):
        self.lines.append(line)
        self.Q.put(line)

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)

    def close(self):
        self.eof.set()
        self.Q.put(None)

    @property
    def closed(self):
        return self.eof.is_set()

    def __iter__(self):
        while True:
            line = self.readline()
            if line is None:
                return
            yield line


class Command:
    '''
    A line-oriented wrapper for running external commands.

    cmd: iterable[str] | callable
        The command to run.

    stdin: None | iterable[str] | True
        The input text, one item for each line, without trailing newline.
        If set to ``True``, stdin will be a writable stream.
        If set to ``None``, stdin is closed after creation.

    stdout: None | bool | callable[str]
        If set to ``None``, stdout will be left as-is (most likely to the tty).
        If set to ``False``, stdout will be silently dropped.
        If set to ``True`` or a callable, stdout will be a readable stream.

    stderr: None | bool | callable[str]
        If set to ``None``, stderr will be left as-is (most likely to the tty).
        If set to ``False``, stderr will be silently dropped.
        If set to ``True`` or a callable, stderr will be a readable stream.

    env: dict[str, str]:
        The environment variables.
    '''

    def __init__(self, cmd,
            stdin=None, stdout=True, stderr=True,
            newline='\n', env=None):

        if callable(cmd):
            self.cmd = cmd
        else:
            self.cmd = [str(token) for token in cmd]

        self.newline = newline

        self.env = env
        self.proc = None
        self.thread = None
        self.returncode = None

        if isinstance(stdin, str):
            stdin = [stdin]

        if stdout is None or isinstance(stdout, bool):
            pass
        else:
            raise TypeError('stdout should be None or bool')

        if stderr is None or isinstance(stderr, bool):
            pass
        else:
            raise TypeError('stderr should be None or bool')

        # Initialize stdin stream
        if stdin is None or stdin is False:
            self.stdin = None

        elif isinstance(stdin, list):
            self.stdin = Stream()
            for line in stdin:
                self.stdin.writeline(line)
            self.stdin.close()

        elif stdin is True:
            self.stdin = Stream()

        # Initialize stdout stream
        if stdout is None or stdout is False:
            self.stdout = None
        else:
            self.stdout = Stream()
            if callable(stdout):
                self.stdout.callback(stdout)

        # Initialize stderr stream
        if stderr is None or stderr is False:
            self.stderr = None
        else:
            self.stderr = Stream()
            if callable(stderr):
                self.stderr.callback(stderr)

        self.io_threads = []

    def __getitem__(self, idx):
        return [self.stdin, self.stdout, self.stderr][idx]

    def run(self, wait=True):
        if callable(self.cmd):
            def worker():
                self.returncode = self.cmd(self.stdin, self.stdout, self.stderr)
                self.stdout.close()
                self.stderr.close()

            self.thread = threading.Thread(target=worker)
            self.thread.daemon = True
            self.thread.start()

        else:
            self.proc = sub.Popen(self.cmd,
                    stdin=None if not self.stdin else sub.PIPE,
                    stdout=None if self.stdout is None else sub.PIPE,
                    stderr=None if self.stderr is None else sub.PIPE,
                    encoding='utf-8', bufsize=1, universal_newlines=True,
                    env=self.env)

            def writer(self_stream, proc_stream):
                for line in self_stream:
                    proc_stream.write(line + self.newline)
                    proc_stream.flush()
                proc_stream.close()

            def reader(self_stream, proc_stream):
                for line in proc_stream:
                    line = line.rstrip()
                    self_stream.writeline(line)
                self_stream.close()

            for (worker, self_stream, proc_stream) in (
                    (writer, self.stdin, self.proc.stdin),
                    (reader, self.stdout, self.proc.stdout),
                    (reader, self.stderr, self.proc.stderr),
                    ):
                if self_stream and proc_stream:
                    t = threading.Thread(target=worker, args=(self_stream, proc_stream))
                    t.daemon = True
                    t.start()
                    self.io_threads.append(t)

        if wait:
            self.wait()

        return self

    def wait(self):
        # Wait for all streams to close
        for idx in (0, 1, 2):
            if self[idx]:
                self[idx].eof.wait()

        # Gracefully wait for threads and child process to finish
        for t in self.io_threads:
            t.join()

        if self.proc:
            self.proc.wait()
            self.returncode = self.proc.returncode

        if self.thread:
            self.thread.join()


cmd = Command


def run(cmd, stdin=None, stdout=True, stderr=True, newline='\n', env=None, wait=True):
    ret = Command(cmd, stdin=stdin, stdout=stdout, stderr=stderr, newline=newline, env=env)
    if wait:
        ret.wait()
    return ret


def pipe(istream, *ostreams):
    def worker(istream, *ostreams):
        for line in istream:
            for ostream in ostreams:
                ostream.writeline(line)

        istream.eof.wait()
        for ostream in ostreams:
            ostream.close()

    t = threading.Thread(target=worker, args=(istream, *ostreams))
    t.daemon = True
    t.start()


def selftest(verbose=True):
    from . import lib_selftest
    section = lib_selftest.section
    EXPECT_EQ = lib_selftest.EXPECT_EQ

    section('stream tests')
    s = Stream()
    s.writeline('line1')
    s.writeline('line2')
    s.writeline('line3')
    EXPECT_EQ(s.closed, False)
    s.close()
    EXPECT_EQ(s.closed, True)
    EXPECT_EQ(s.lines, ['line1', 'line2', 'line3'])

    s = Stream()
    lines = ['line1', 'line2', 'line3']
    s.writelines(lines)
    s.close()
    for nr, line in enumerate(s):
        EXPECT_EQ(lines[nr], line)

    section('Simple stdout tests')
    p = cmd('seq 5'.split())
    p.run(wait=False).wait()
    EXPECT_EQ(p.stdout.lines, ['1', '2', '3', '4', '5'])

    section('stdin tests')
    p = cmd('nl -w 1 -s :'.split(), stdin=['hello', 'world'])
    p.run(wait=False).wait()
    EXPECT_EQ(p.stdout.lines, ['1:hello', '2:world'])

    section('pipe tests')
    p1 = cmd('nl -w 1 -s :'.split(), stdin=['hello', 'world'])
    p2 = cmd('nl -w 1 -s /'.split(), stdin=True)
    pipe(p1.stdout, p2.stdin)

    p1.run()
    EXPECT_EQ(p1.stdout.lines, ['1:hello', '2:world'])
    EXPECT_EQ(p2.stdin.lines, ['1:hello', '2:world'])
    p2.run(wait=False)

    p2.wait()
    EXPECT_EQ(p2.stdout.lines, ['1/1:hello', '2/2:world'])

    section('callable + pipe tests')

    def proc(i, o, e):
        for line in i:
            o.writeline(line)
            e.writeline(line)
        return 2024

    p1 = cmd(proc, stdin=['hello', 'world'])
    p2 = cmd('nl -w 1 -s :'.split(), stdin=True)
    p3 = cmd('nl -w 1 -s /'.split(), stdin=True)
    pipe(p1.stdout, p2.stdin)
    pipe(p1.stderr, p3.stdin)

    p1.run()
    p2.run()
    p3.run()

    EXPECT_EQ(p1.returncode, 2024)
    EXPECT_EQ(p2.stdout.lines, ['1:hello', '2:world'])
    EXPECT_EQ(p3.stdout.lines, ['1/hello', '2/world'])

    section('loopback test')
    def pi(i, o, e):
        # BBP

        def bbp(k):
            return (1 / 16 ** k) * (
                    (4 / (8 * k + 1)) -
                    (2 / (8 * k + 4)) -
                    (1 / (8 * k + 5)) -
                    (1 / (8 * k + 6))
                    )

        for line in i:
            if isinstance(line, int):
                n = line
                o.writeline((n, 1, bbp(0)))

            else:
                n, k, s = line
                if n == k:
                    o.writeline(s)
                    break

                o.writeline((n, k + 1, s + bbp(k)))

    p = cmd(pi, stdin=True)
    pipe(p.stdout, p.stdin)
    p.stdin.writeline(11)
    p.run()
    for line in p.stdout.lines:
        print(line)
    EXPECT_EQ(str(p.stdout.lines[-1]), '3.141592653589793')
