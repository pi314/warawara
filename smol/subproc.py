import queue
import subprocess as sub
import threading


__all__ = ['stream', 'command', 'run', 'pipe']
__all__ += ['TimeoutExpired', 'AlreadyRunningError']
__all__ += ['RunMocker']


TimeoutExpired = sub.TimeoutExpired


class AlreadyRunningError(Exception):
    def __init__(self, cmd):
        prog = cmd.cmd[0].__name__ + '()' if callable(cmd.cmd[0]) else cmd.cmd[0]
        super().__init__(' '.join(
            [prog] + cmd.cmd[1:]))


class EventBroadcaster:
    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def broadcast(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)


class QueueEventAdapter:
    def __init__(self, Q):
        self.Q = Q

    def __call__(self, line):
        self.Q.put(line)


class stream:
    def __init__(self):
        self.queue = queue.Queue()
        self.keep = False
        self.lines = []
        self.eof = threading.Event()
        self.hub = EventBroadcaster()

    def welcome(self, subscriber):
        if isinstance(subscriber, (list, tuple)):
            for s in subscriber:
                self.welcome_one(s)
        else:
            self.welcome_one(subscriber)

    def welcome_one(self, subscriber):
        if subscriber is True:
            self.keep = True

        else:
            handler = None
            if hasattr(subscriber, 'put'):
                handler = QueueEventAdapter(subscriber)
            elif callable(subscriber):
                handler = subscriber

            if handler:
                self.hub += handler
            else:
                raise TypeError('Invalid subscriber value: {}'.format(repr(subscriber)))

    def readline(self):
        line = self.queue.get()
        return line

    def writeline(self, line):
        if self.keep:
            self.lines.append(line)

        self.queue.put(line)
        self.hub.broadcast(line)

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)

    def close(self):
        self.eof.set()
        self.queue.put(None)

    @property
    def closed(self):
        return self.eof.is_set()

    @property
    def empty(self):
        return not self.lines and not self.queue.empty()

    def __bool__(self):
        return not self.empty

    def __len__(self):
        return len(self.lines)

    def __iter__(self):
        if self.closed:
            yield from self.lines

        else:
            while True:
                line = self.readline()
                if line is None:
                    break
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
        Otherwise, stdin will be a subproc.stream object, stdin.close() needs to be called manually.

        If a Queue is provided, stdin.task_done() will be called for each item.

    stdout: None | False | True | callable[str] | Queue
        The stdout "subscribers".
        Default: True.

        If set to ``True`` or a callable, stdout will be a subproc.stream object.
        If set to ``None``, stdout will be left as-is (most likely to the tty).
        If set to other falsy-values, stdout will be silently dropped.
        If set to ``Queue`` object, each line will be put into the queue object.

        Multiple objects could be provided at once for output duplication.
        E.g. tuple(print, queue.Queue())

    stderr: None | False | True | callable[str] | Queue
        The stderr "subscribers".
        Default: True.

        If set to ``True`` or a callable, stderr will be a subproc.stream object .
        If set to ``None``, stderr will be left as-is (most likely to the tty).
        If set to ``False``, stderr will be silently dropped.
        If set to ``Queue`` object, each line will be put into the queue object.

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
        self.exception = None
        self.killed = threading.Event()
        self.returncode = None

        if isinstance(stdin, str):
            stdin = [stdin]

        # Initialize stdin stream
        self.stdin = stream()
        self.stdin.keep = True
        if stdin is None or stdin is False:
            self.proc_stdin = None
            self.stdin.close()
            self.user_stdin = []
        else:
            self.proc_stdin = sub.PIPE
            self.user_stdin = stdin

        # Initialize stdout stream
        self.stdout = stream()
        if stdout is None:
            self.proc_stdout = None
            self.stdout.close()
        elif stdout is False:
            self.proc_stdout = sub.DEVNULL
            self.stdout.close()
        else:
            self.proc_stdout = sub.PIPE
            self.stdout.keep = False
            self.stdout.welcome(stdout)

        # Initialize stderr stream
        self.stderr = stream()
        if stderr is None:
            self.proc_stderr = None
            self.stderr.close()
        elif stderr is False:
            self.proc_stderr = sub.DEVNULL
            self.stderr.close()
        else:
            self.proc_stderr = sub.PIPE
            self.stderr.keep = False
            self.stderr.welcome(stderr)

        self.io_threads = []

    def __getitem__(self, idx):
        return [self.stdin, self.stdout, self.stderr][idx]

    def __enter__(self):
        return self.run(wait=False)

    def __exit__(self, exc_type, exc_value, traceback):
        self.stdin.close()
        self.stdout.close()
        self.stderr.close()
        self.wait()

    def run(self, wait=True, timeout=None):
        if self.proc or self.thread:
            raise AlreadyRunningError(self)

        if callable(self.cmd[0]):
            def worker():
                try:
                    self.returncode = self.cmd[0](self, *self.cmd[1:])
                except Exception as e:
                    self.exception = e

                self.stdin.close()
                self.stdout.close()
                self.stderr.close()

            self.thread = threading.Thread(target=worker)
            self.thread.daemon = True
            self.thread.start()

        else:
            self.proc = sub.Popen(self.cmd,
                    stdin=self.proc_stdin,
                    stdout=self.proc_stdout,
                    stderr=self.proc_stderr,
                    encoding='utf-8', bufsize=1, universal_newlines=True,
                    env=self.env)

            def writer(self_stream, proc_stream):
                for line in self_stream:
                    proc_stream.write(line + self.newline)
                    proc_stream.flush()
                proc_stream.close()

            def reader(self_stream, proc_stream):
                for line in proc_stream:
                    line = line.rstrip(self.newline)
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

        if wait or timeout:
            self.wait(timeout)

        return self

    def wait(self, timeout=None):
        # Wait for child process to finish
        if self.proc:
            self.proc.wait(timeout)
            self.returncode = self.proc.returncode

        if self.thread:
            self.thread.join(timeout)

        # Wait too early
        if self.proc is None and self.thread is None:
            return

        if self.exception:
            raise self.exception

        # Wait for all streams to close
        self.stdin.eof.wait()
        self.stdout.eof.wait()
        self.stderr.eof.wait()

        # Gracefully wait for threads to finish
        for t in self.io_threads:
            t.join()

    def kill(self):
        if self.proc:
            self.proc.kill()
            self.proc.wait()
            for proc_stream in (
                    self.proc.stdin,
                    self.proc.stdout,
                    self.proc.stderr
                    ):
                if proc_stream:
                    proc_stream.close()

            self.returncode = self.proc.returncode

        if self.thread:
            self.killed.set()
            self.thread.join()


def run(cmd, stdin=None, stdout=True, stderr=True, newline='\n', env=None, wait=True, timeout=None):
    ret = command(cmd, stdin=stdin, stdout=stdout, stderr=stderr, newline=newline, env=env)
    ret.run(wait=wait, timeout=timeout)
    return ret


def pipe(istream, *ostreams):
    def worker(istream, ostreams):
        for line in istream:
            for ostream in ostreams:
                ostream.writeline(line)

        istream.eof.wait()
        for ostream in ostreams:
            ostream.close()

    t = threading.Thread(target=worker, args=(istream, ostreams))
    t.daemon = True
    t.start()


class RunMocker:
    def __init__(self):
        self.rules = {}

    def register(self, cmd, callback=None, stdout=None, stderr=None, returncode=None):
        if all((callback is None, stdout is None, stderr is None, returncode is None)):
            raise ValueError('Meaningless mock')

        if callback is not None and any((
                stdout is not None,
                stderr is not None,
                returncode is not None
                )):
            raise ValueError('Ambiguous mock')

        if not isinstance(cmd, str):
            cmd = tuple(cmd)

        if cmd not in self.rules:
            self.rules[cmd] = []

        if stdout is not None or stderr is not None or returncode is not None:
            def simple_prog(proc, *args):
                if stdout:
                    proc.stdout.writelines(stdout)
                if stderr:
                    proc.stderr.writelines(stderr)
                return returncode

            callback = simple_prog

        self.rules[cmd].append(callback)
        return self

    @classmethod
    def match_pattern(cls, pattern, cmd):
        if len(pattern) != len(cmd):
            return None

        args = []
        for parg, carg in zip(pattern, cmd):
            if parg == carg:
                pass
            elif parg == '{}':
                args.append(carg)
            else:
                return None

        return args

    def __call__(self, cmd, stdin=None, stdout=True, stderr=True, newline='\n', env=None, wait=True, timeout=None):
        matched_pattern = None
        matched_args = []
        for rule in self.rules.items():
            pattern = rule[0]
            callbacks = rule[1]

            if isinstance(pattern, str):
                continue

            args = type(self).match_pattern(pattern, cmd)
            if args:
                matched_pattern = pattern
                matched_args = args

        if not matched_pattern:
            if cmd[0] in self.rules:
                matched_pattern = cmd[0]
                matched_args = cmd[1:]

        if not matched_pattern:
            raise ValueError('Unregistered command: {}'.format(cmd))

        matched_callbacks = self.rules[matched_pattern]

        callback = matched_callbacks[0]
        if len(matched_callbacks) > 1:
            matched_callbacks.pop(0)

        p = command([callback] + matched_args, stdin=stdin, stdout=stdout, stderr=stderr, newline=newline, env=env)
        p.run(wait=wait, timeout=timeout)
        return p
