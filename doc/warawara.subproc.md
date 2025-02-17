warawara.subproc
===============================================================================

This document describes the API set provided by `warawara.subproc`.

For the index of this package, see [warawara.md](warawara.md).

`command()`
-------------------------------------------------------------------------------
A line-oriented wrapper for running external commands.

__Parameters__
```python
command(cmd, *, stdin=None, stdout=True, stderr=True, newline='\n', env=None, wait=True, timeout=None)
```


`run()`
-------------------------------------------------------------------------------
Runs a command and returns the result,
or triggers a command and returns the promise object.

__Parameters__
```python
run(cmd, *, stdin=None, stdout=True, stderr=True, newline='\n', env=None, wait=True, timeout=None)
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
RunMocker.__call__(cmd, *, stdin=None, stdout=True, stderr=True, newline='\n', env=None, wait=True, timeout=None)
```
