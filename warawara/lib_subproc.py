import queue
import subprocess as sub
import threading

from .lib_itertools import is_iterable

from .internal_utils import exporter
export, __all__ = exporter()


export('TimeoutExpired')
TimeoutExpired = sub.TimeoutExpired


@export
class AlreadyRunningError(Exception):
    def __init__(self, cmd):
        if callable(cmd.cmd[0]):
            prog = cmd.cmd[0].__name__ + '()'
        else:
            prog = cmd.cmd[0]

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


@export
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

    def read(self):
        data = self.queue.get()
        return data

    def readline(self):
        return self.read()

    def write(self, data, *, suppress=True):
        if self.closed:
            if suppress:
                return
            raise BrokenPipeError('stream already closed')

        if self.keep:
            self.lines.append(data)

        self.queue.put(data)
        self.hub.broadcast(data)

    def writeline(self, line, *, suppress=True):
        self.write(line, suppress=suppress)

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
        return not self.lines and self.queue.empty()

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


@export
class command:
    '''
    A line-oriented wrapper for running external commands.

    cmd: tuple[str] | list[str] | callable
        The command to run.

    stdin: None | iterable[str] | Queue | True
        The input text, one item for each line, without trailing newline.
        Default: None.

        If set to ``None`` or ``False``, stdin is closed after creation.
        If set to a ``list`` or a ``tuple``, stdin is closed after data fed into the process.
        Otherwise, stdin.close() needs to be called manually.

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

    def __init__(self, cmd=None, *,
                 stdin=None, stdout=True, stderr=True,
                 encoding='utf8', rstrip='\r\n',
                 bufsize=-1,
                 env=None):

        if cmd and isinstance(cmd, str):
            cmd = [cmd]
        elif callable(cmd):
            cmd = [cmd]
        elif isinstance(cmd, (tuple, list)):
            pass
        else:
            raise ValueError('Invalid command:' + repr(cmd))

        if not cmd:
            raise ValueError('command is empty')

        if callable(cmd[0]):
            self.cmd = [token for token in cmd]
        else:
            self.cmd = [str(token) for token in cmd]

        self.encoding = encoding
        self.bufsize = bufsize
        self.rstrip = rstrip

        self.env = env
        self.proc = None
        self.thread = None
        self.exception = None
        self.killed = threading.Event()
        self.returncode = None

        if isinstance(stdin, (str, bytes, bytearray)):
            stdin = [stdin]

        # Initialize stdin stream
        self.stdin = stream()
        self.stdin.keep = True
        self.stdin_queue = None
        self.stdin_autoclose = False
        if stdin is None or stdin is False:
            self.proc_stdin = None
            self.stdin.close()
            self.user_stdin = []
        else:
            self.proc_stdin = sub.PIPE
            if isinstance(stdin, queue.Queue):
                self.stdin_queue = stdin
            elif is_iterable(stdin):
                for line in stdin:
                    self.stdin.write(line)
                self.stdin_autoclose = True

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
            if self.encoding == False:
                # binary mode
                kwargs = {
                        'bufsize': 2 if self.bufsize == 1 else self.bufsize,
                        'text': False,
                        }
            else:
                kwargs = {
                        'bufsize': 1,
                        'encoding': self.encoding,
                        'errors': 'backslashreplace',
                        }

            self.proc = sub.Popen(
                    self.cmd,
                    stdin=self.proc_stdin,
                    stdout=self.proc_stdout,
                    stderr=self.proc_stderr,
                    env=self.env, **kwargs)

            def writer(self_stream, proc_stream):
                for line in self_stream:
                    if self.encoding == False:
                        proc_stream.write(line)
                    elif isinstance(line, (bytes, bytearray)):
                        proc_stream.buffer.write(line)
                    else:
                        proc_stream.write(line + '\n')
                    proc_stream.flush()
                proc_stream.close()

            def reader(self_stream, proc_stream):
                if self.encoding != False:
                    # text
                    for line in proc_stream:
                        line = line.rstrip(self.rstrip)
                        self_stream.writeline(line)

                else:
                    # binary
                    while self.poll() is None:
                        data = proc_stream.read(
                                -1
                                if self.bufsize < 0
                                else (self.bufsize or 1)
                                )

                        if not data:
                            continue

                        self_stream.write(data)

                    # Read all remaining data left in stream
                    data = proc_stream.read()
                    if data:
                        self_stream.writeline(data)

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

        # Pull data from stdin_queue and feed into stdin stream
        if self.stdin_queue:
            def feeder():
                while True:
                    self.stdin.writeline(self.stdin_queue.get())
                    self.stdin_queue.task_done()

            t = threading.Thread(target=feeder)
            t.daemon = True
            t.start()

        elif self.stdin_autoclose:
            self.stdin.close()

        if wait or timeout:
            self.wait(timeout)

        return self

    def poll(self):
        if self.proc:
            return self.proc.poll()
        if self.thread:
            return self.returncode
        return False

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


@export
def run(cmd=None, *,
        stdin=None, stdout=True, stderr=True,
        encoding='utf8', rstrip='\r\n',
        bufsize=-1,
        env=None,
        wait=True, timeout=None):
    ret = command(cmd,
                  stdin=stdin, stdout=stdout, stderr=stderr,
                  encoding=encoding,
                  rstrip=rstrip, env=env)
    ret.run(wait=wait, timeout=timeout)
    return ret


@export
def pipe(istream, *ostreams):
    if istream.closed:
        raise EOFError('istream already closed')

    for ostream in ostreams:
        if ostream.closed:
            raise BrokenPipeError('ostream already closed')

    def worker(istream, ostreams):
        exception = None
        try:
            for line in istream:
                for ostream in ostreams:
                    ostream.write(line)

        except Exception as e:
            exception = e
            istream.close()

        istream.eof.wait()
        for ostream in ostreams:
            ostream.close()

        if exception:
            raise exception

    t = threading.Thread(target=worker, args=(istream, ostreams))
    t.daemon = True
    t.start()


@export
class RunMocker:
    def __init__(self):
        self.rules = {}

    def register(self, cmd, callback=None, *, stdout=None, stderr=None, returncode=None):
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

    def __call__(self, cmd, *,
                 stdin=None, stdout=True, stderr=True,
                 encoding='utf8', rstrip='\r\n',
                 bufsize=-1,
                 env=None,
                 wait=True, timeout=None):
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

        p = command([callback] + matched_args,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    encoding=encoding, rstrip=rstrip,
                    bufsize=bufsize,
                    env=env)
        p.run(wait=wait, timeout=timeout)
        return p
