warawara.subproc
===============================================================================

This document describes the API set provided by `warawara.subproc`.

For the index of this package, see [warawara.md](warawara.md).

`command()`
-------------------------------------------------------------------------------
Creates a line-oriented `command` object for interacing with the specified command.

The command is not started after creation.  
You could prepare data for stdin, or creating pipes from stdout/stderr before running.

A `command` object holds an external command, or a `callable` with parameters.  
They could be mixed together in a pipeline in order to complete complex tasks.

For example, you could get stdout from `ls -1` line by line,
add prefix to all of them,
and pipe the results into `nl` to number them.

It's like writing a pipeline with a lot of `awk`, `sed`, `grep`, etc, all in Python.

__Parameters__
```python
command(self, cmd=None, *,
        stdin=None, stdout=True, stderr=True,
        encoding='utf8', rstrip='\r\n',
        bufsize=-1,
        env=None)
```

*   `cmd`
    -   If `cmd` is a `tuple` or a `list`, it's converted into `[cmd]` and goes to the following cases.
    -   If `cmd` is a `[str, ...]`, the first item is taken as the command,
        and the remaining items are taken as arguments.
    -   If `cmd` is a `[callable, ...]`, the first item is taken as the command,
        and the remaining items are taken as arguments.
        +   The callable should take `len(cmd)` parameters.
        +   The first parameter of the callable is `proc`, which is the command object itself.
        +   The remaining parameters are assigned with the remaining arguments.
    -   Otherwise, `ValueError` is raised.

    -   Examples
        +   `'true'`
        +   `['ls', '-a', '-1']`
        +   Callable
            *   `lambda proc: ...`
            *   `[(lambda proc, arg1, arg2: ...), 'bar', 'baz']` (a callable with arguments)

*   `stdin` (default: `None`)
    -   If `stdin` is `None` or `False`, the stream is closed.
    -   If `stdin` is a `str`, `bytes`, or a `bytearray`, it's converted into `[stdin]` and goes to the following cases.
    -   If `stdin` is a `tuple` or a `list`, each item is treated as one line of text input.
        +   The stream is left open and accepts more input, and it's closed upon `run()`.
    -   If `stdin` is `True`, the stream is left open and wait for data input.
    -   If `stdin` is a `queue.Queue`, the stream is left open
        and the process pulls data from the given `Queue` object and feed into `stdin`.

*   `stdout` (default: `True`)
    -   If `stdout` is `None`, the stream is forwarded to the tty.
    -   If `stdout` is `False`, the stream is closed and outputs are silently dropped.
    -   If `stdout` is `True`, the output data is kept in the stream object.
    -   If `stdout` is a `callable`, the callable is called for each line as argument.
    -   If `stdout` is a `queue.Queue`, each line of output is put into the `Queue` object.
    -   If `stdout` is a `tuple` or a `list`, output is duplicated to each object.
    -   Examples
        +   `stdout=lambda line: ...`
        +   `stdout=tuple(print, queue.Queue())`

*   `stderr` (default: `True`)
    -   See `stdout`.

*   `encoding` (default: `'utf8'`)
    -   If `encoding` is `False`, the process is opened in binary mode.

*   `rstrip` (default: `'\r\n'`)
    -   In text mode (`encoding != False`), each line will be `rstrip()`ed with `rstrip` value

*   `bufsize` (default: `-1`)
    -   `bufsize` is only meaningful when encoding is `False`.
    -   This value controls the rough size of underlying buffer.

*   `env` (default: None)
    -   Environment variables.
    -   By default, child processs inherits environment variables from parent proess.

A `command` object has the following methods and properties:

*   `run(wait=True)`: run the command and returns the command object itself.
    -   The `wait` argument is passed to `wait()` method, see below.
*   `poll()`: check the process status and return the status code.
*   `wait(timeout=None)`: wait the process to finish for `timeout` seconds.
    -   If `timeout` is `True` or `None`, it waits for the command to finish.
    -   If `timeout` is `False`, it returns immediately.
    -   If `timeout` is an `int` or a `float`, it waits for the specified seconds.
    -   Otherwise, `TypeError` is raised.
*   `signal(signal)`: send `signal` to the process.
*   `kill(signal=SIGKILL)`: send `signal`, wait for the process to stop, and close all streams.
*   `signaled`: stores the received signal.
    -   It's a subclass of `threading.Event` thus can be `.wait()`.
*   `killed`: an alias to `signaled`.

Each stream object (i.e. `command.stdin`, `command.stdout`, and `command.stderr`)
has the following methods and properties:

*   `read()`: read one line or a block of data from the stream.
*   `readline()`: an alias to `read()`.
*   `write(data)`: write one line or a block of data to the stream.
*   `writeline(line)`: an alias to `write()`.
*   `writelines(lines)`: write each line in `lines` with `writeline()`.
*   `close()`: close the stream.
*   `closed`: indicate if the stream is already closed.
*   `empty`: indicate if the stream is empty.
*   `lines`: all lines or data blocks flowed through the stream.
*   `__len__()`
*   `__iter__()`


`run()`
-------------------------------------------------------------------------------
Creates a `command` object and runs it.

__Parameters__
```python
run(cmd=None, *,
    stdin=None, stdout=True, stderr=True,
    encoding='utf8', rstrip='\r\n',
    bufsize=-1,
    env=None,
    wait=True, timeout=None)
```


`pipe()`
-------------------------------------------------------------------------------
Connect input/output streams together.

__Parameters__
```python
pipe(istream, *ostreams)
```

Class `RunMocker`
-------------------------------------------------------------------------------

__Parameters__
```python
RunMocker()
RunMocker.register(cmd, callback=None, *, stdout=None, stderr=None, returncode=None)
RunMocker.__call__(self, cmd, *,
                   stdin=None, stdout=True, stderr=True,
                   encoding='utf8', rstrip='\r\n',
                   bufsize=-1,
                   env=None,
                   wait=True, timeout=None)
```
