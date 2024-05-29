import queue
import subprocess as sub
import threading


__all__ = ['stream', 'command', 'run', 'pipe']


class stream:
    def __init__(self):
        self.Q = queue.Queue()
        self.__lines = []
        self.subscriber_list = []
        self.eof = threading.Event()

    def welcome(self, subscriber):
        if isinstance(subscriber, (list, tuple)):
            for s in subscriber:
                self.welcome(s)
            return

        if subscriber is not True:
            ok = False
            if hasattr(subscriber, 'put'):
                ok = True
            if callable(subscriber):
                ok = True

            if ok:
                self.subscriber_list.append(subscriber)

            else:
                raise TypeError('Invalid subscriber value: {}'.format(repr(subscriber)))

    @property
    def lines(self):
        return self.__lines

    def readline(self):
        line = self.Q.get()
        return line

    def writeline(self, line):
        self.lines.append(line)
        self.Q.put(line)
        for s in self.subscriber_list:
            if hasattr(s, 'put'):
                s.put(line)
            elif callable(s):
                s(line)

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)

    def close(self):
        self.eof.set()
        self.Q.put(None)

    @property
    def closed(self):
        return self.eof.is_set()

    @property
    def empty(self):
        return not self.lines

    def __bool__(self):
        return not self.empty

    def __len__(self):
        return len(self.lines)

    def __iter__(self):
        while True:
            line = self.readline()
            if line is None:
                return
            yield line


class command:
    '''
    A line-oriented wrapper for running external commands.

    cmd: iterable[str] | callable
        The command to run.

    stdin: None | iterable[str] | Queue | True
        The input text, one item for each line, without trailing newline.
        Default: None.

        If set to ``None`` or ``False``, stdin is closed after creation.
        If set to a ``list`` or a ``tuple``, stdin is closed after data fed into the process.
        Otherwise, stdin will be a subproc.stream, stdin.close() needs to be called manually.

        If a Queue is provided, stdin.task_done() will be called for each item.

    stdout: None | False | True | callable[str] | Queue
        The stdout "subscribers".
        Default: True.

        If set to ``True`` or a callable, stdout will be a subproc.stream .
        If set to ``None``, stdout will be left as-is (most likely to the tty).
        If set to other falsy-values, stdout will be silently dropped.
        If set to ``Queue``, each line will be put into the queue object.

        Multiple objects could be provided at once for output duplication.
        E.g. tuple(print, queue.Queue())

    stderr: None | False | True | callable[str] | Queue
        The stderr "subscribers".
        Default: True.

        If set to ``True`` or a callable, stderr will be a subproc.stream .
        If set to ``None``, stderr will be left as-is (most likely to the tty).
        If set to ``False``, stderr will be silently dropped.
        If set to ``Queue``, each line will be put into the queue object.

        Multiple objects could be provided at once for output duplication.
        E.g. tuple(print, queue.Queue())

    env: dict[str, str]:
        The environment variables.
    '''

    def __init__(self, cmd,
            stdin=None, stdout=True, stderr=True,
            newline='\n', env=None):

        if callable(cmd):
            cmd = [cmd]

        if callable(cmd[0]):
            self.cmd = [token for token in cmd]
        else:
            self.cmd = [str(token) for token in cmd]

        if not self.cmd:
            raise ValueError('command is empty')

        self.newline = newline

        self.env = env
        self.proc = None
        self.thread = None
        self.returncode = None

        if isinstance(stdin, str):
            stdin = [stdin]

        # Initialize stdin stream
        self.stdin = stream()
        if stdin is None or stdin is False:
            self.stdin.close()
            self.user_stdin = []
        else:
            self.user_stdin = stdin

        # Initialize stdout stream
        self.stdout = stream()
        if stdout is None or stdout is False:
            self.stdout.close()
        else:
            self.stdout.welcome(stdout)

        # Initialize stderr stream
        self.stderr = stream()
        if stderr is None or stderr is False:
            self.stderr.close()
        else:
            self.stderr.welcome(stderr)

        self.io_threads = []

    def __getitem__(self, idx):
        return [self.stdin, self.stdout, self.stderr][idx]

    def run(self, wait=True, timeout=None):
        if callable(self.cmd[0]):
            def worker():
                self.returncode = self.cmd[0](self, *self.cmd[1:])
                self.stdin.close()
                self.stdout.close()
                self.stderr.close()

            self.thread = threading.Thread(target=worker)
            self.thread.daemon = True
            self.thread.start()

        else:
            self.proc = sub.Popen(self.cmd,
                    stdin=None if self.stdin.closed and self.stdin.empty else sub.PIPE,
                    stdout=None if self.stdout.closed else sub.PIPE,
                    stderr=None if self.stderr.closed else sub.PIPE,
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
                proc_stream.close()

            for (worker, self_stream, proc_stream) in (
                    (writer, self.stdin, self.proc.stdin),
                    (reader, self.stdout, self.proc.stdout),
                    (reader, self.stderr, self.proc.stderr),
                    ):
                if self_stream is not None and proc_stream is not None:
                    t = threading.Thread(target=worker, args=(self_stream, proc_stream))
                    t.daemon = True
                    t.start()
                    self.io_threads.append(t)

        # Feed user stdin and close the stream
        if self.user_stdin is not True:
            def feeder():
                if isinstance(self.user_stdin, queue.Queue):
                    while True:
                        self.stdin.writeline(self.user_stdin.get())
                        self.user_stdin.task_done()

                else:
                    for line in self.user_stdin:
                        self.stdin.writeline(line)
                    self.stdin.close()

            t = threading.Thread(target=feeder)
            t.daemon = True
            t.start()

        if wait:
            self.wait(timeout)

        return self

    def wait(self, timeout=None):
        # Wait for child process to finish
        if self.proc:
            self.proc.wait(timeout)
            self.returncode = self.proc.returncode

        if self.thread:
            self.thread.join(timeout)

        # Wait for all streams to close
        self.stdin.eof.wait()
        self.stdout.eof.wait()
        self.stderr.eof.wait()

        # Gracefully wait for threads to finish
        for t in self.io_threads:
            t.join()


def run(cmd, stdin=None, stdout=True, stderr=True, newline='\n', env=None, wait=True):
    ret = command(cmd, stdin=stdin, stdout=stdout, stderr=stderr, newline=newline, env=env)
    ret.run(wait=wait)
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
