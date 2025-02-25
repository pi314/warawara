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
    -   If `cmd` is a `str`, it's taken as a single-word external command.
    -   If `cmd` is a `callable`, it's taken without arguments.
    -   If `cmd` is a `tuple` or a `list`,
        the first item is taken as the command
        and the remaining arguments.
    -   Otherwise, `ValueError` is raised.

    -   Examples
        +   `'true'`
        +   `['ls', '-a', '-1']`
        +   `foo` (a callable)
        +   `[foo, 'bar', 'baz']` (a callable with arguments)

*   `stdin`
    -   If `stdin` is `None` or `False`, the stream is closed.
    -   If `stdin` is a `str`, `bytes`, or a `bytearray`, it's converted into `[stdin]` and goes to the next case.
    -   If `stdin` is a `tuple` or a `list`, each item is treated as one line of text input.
        +   The stream is left open and accepts more input, and it's closed upon `run()`.
    -   If `stdin` is `True`, the stream is left open and wait for data input.
    -   If `stdin` is a `queue.Queue`, the stream is left open
        and the process pulls data from the given `Queue` object and feed into `stdin`.


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
