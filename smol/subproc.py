import queue
import subprocess as sub
import threading


__all__ = ['stream', 'command', 'run', 'pipe']


class stream:
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
        return line

    def writeline(self, line):
        self.lines.append(line)
        self.Q.put(line)
        for callback in self.callbacks:
            callback(line)

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

        if stdout is None or isinstance(stdout, bool) or callable(stdout):
            pass
        else:
            raise TypeError('stdout should be None or bool')

        if stderr is None or isinstance(stderr, bool) or callable(stderr):
            pass
        else:
            raise TypeError('stderr should be None or bool')

        # Initialize stdin stream
        self.stdin = stream()
        if stdin is None or stdin is False:
            self.stdin.close()

        elif isinstance(stdin, list):
            for line in stdin:
                self.stdin.writeline(line)
            self.stdin.close()

        # Initialize stdout stream
        self.stdout = stream()
        if stdout is None or stdout is False:
            self.stdout.close()
        elif callable(stdout):
            self.stdout.callback(stdout)

        # Initialize stderr stream
        self.stderr = stream()
        if stderr is None or stderr is False:
            self.stderr.close()
        elif callable(stderr):
            self.stderr.callback(stderr)

        self.io_threads = []

    def __getitem__(self, idx):
        return [self.stdin, self.stdout, self.stderr][idx]

    def run(self, wait=True, timeout=None):
        if callable(self.cmd[0]):
            def worker():
                self.returncode = self.cmd[0](self, *self.cmd[1:])
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
