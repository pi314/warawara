iroiro
===============================================================================

A swiss-knife-like library that collects cute utilities for my other projects.

This library only depends on Python standard library and Python itself.
It's functionalities will not depend on any third-party packages in a foreseeable future.

Examples:

```python
# color strings
import iroiro
iroiro.orange('TEXT')   # \033[38;5;214mTEXT\033[m

# Invoke external command and retrieve the result.
p = iroiro.run(['seq', '5'])
p.stdout.lines  # ['1', '2', '3', '4', '5']

# Invoke external command and retrieve the result in a non-blocking manner.
# Functions could be used as command, so they could be mixed in pipe line.
p1 = iroiro.command(['seq', '5'])

def func(streams, *args):
    for line in streams[0]:
        streams[1].writeline('iro: {}'.format(line))

p2 = iroiro.command(func, stdin=True)

iroiro.pipe(p1.stdout, p2.stdin)
p1.run()
p2.run()
p2.stdout.lines   # ['iro: 1', 'iro: 2', 'iro: 3', 'iro: 4', 'iro: 5']
```

From my own perspective, Python's subprocess interface is not friendly enough
for simple uses.

For more detailed API usage, see [doc/iroiro.md](doc/iroiro.md)


Installation
-------------------------------------------------------------------------------
```console
sh$ pip3 install iroiro
```

Or just copy the whole folder to your machine, and add its path to `sys.path`:

```python
import sys
sys.path.insert(0, '/the/path/to/iroiro')
import iroiro
sys.path.pop(0)
```


Testing
-------------------------------------------------------------------------------
*   Through `Makefile`:

    ```console
    sh$ make run
    sh$ make run VERBOSE=1
    ```

    -   To a specific Python version, if [`uv`](https://github.com/astral-sh/uv) is available:

        ```console
        sh$ make run PYTHON=3.9
        ```

*   With built-in [`unittest`](https://docs.python.org/3/library/unittest.html):

    ```console
    sh$ python3 -m unittest | cat
    ```

*   With [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/):

    ```console
    sh$ pipx install pytest-cov --include-deps
    sh$ pytest --cov=iroiro --cov-report=html
    ```

    -   With manually installed `pytest-cov`:

        ```console
        sh$ pipx install pytest
        sh$ pipx runpip pytest install pytest-cov
        sh$ pytest --cov=iroiro --cov-report=html
        ```
        The use case is you only have `python3.7` and `pip` access in a limited environment.
