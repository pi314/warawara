# iroiro

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


## Installation

`iroiro` is on [pypi](https://pypi.org/project/iroiro/):
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


### Shell Utils

`iroiro` comes with several shell utilities, invoke `iroiro` without arguments
to get the list, and run them as sub-command:
```console
sh$ iroiro
iroiro
decolor
nowrap
ntfy
palette
rainbow
sponge
```
```console
sh$ iroiro rainbow
(rainbow)
```

In order to not conflicting with your shell utilities
(e.g. `sponge` from [`moreutils`](https://joeyh.name/code/moreutils/)),
`iroiro` does not install scripts except `iroiro` itself.
Instead, run `iroiro path` to get the shipped/installed `bin/` path.

For example, if `iroiro` is installed through `pipx`, the output might look like this:

```console
sh$ iroiro path
/Users/you/.local/pipx/venvs/iroiro/lib/python3.14/site-packages/iroiro/bin
```

Add it into `$PATH` at the desired position in your shell config to make it permanent.

If the installed path is subjected to change, you can make it dynamic:
```sh
# To place it at the 1st path,
if command -v iroiro >/dev/null 2&>1; then
    export PATH="$(iroiro path)":"$PATH"
fi

# To placed it before certain path,
if command -v iroiro >/dev/null 2&>1; then
    export PATH="$(echo "$PATH" | \
        tr ':' '\n' | \
        awk '$0~/\.local\/bin/{ print ":" "'"$(iroiro path)"'" } { print ":" $0 }' | \
        tr -d '\n' | \
        sed 's/^://')"
fi
```

For more precised control, you can pick certain commands,
and manually create soft links
or small snippets into your self-managed `bin` folder:
```sh
#!/usr/bin/env sh

exec iroiro nowrap "$@"
```

Instead of `$PATH`, you might want to use alias to manage them.
`iroiro alias` shows a sample snippet for reference:
```console
sh$ iroiro alias
alias iroiro='iroiro iroiro'
alias decolor='iroiro decolor'
alias nowrap='iroiro nowrap'
alias ntfy='iroiro ntfy'
alias palette='iroiro palette'
alias rainbow='iroiro rainbow'
alias sponge='iroiro sponge'
```

You can do some processing beforing evaluating the output:
```sh
eval "$(iroiro alias | grep -v sponge)"
```

If alias is not suitable for you, and you don't want to deploy relay scripts,
`iroiro bin` could be used to modify those scripts in-place.

```console
sh$ iroiro bin list
enabled │ decolor
enabled │ nowrap
enabled │ ntfy
enabled │ palette
enabled │ rainbow
enabled │ sponge
```

`iroiro bin` without other arguments launchs an interactive interface.
Modifications are taking effect immediately, there's no 2nd confirmation.
```console
sh$ iroiro bin
  enabled  │ decolor
  enabled  │ nowrap
> disabled │ ntfy
  enabled  │ palette
  enabled  │ rainbow
  enabled  │ sponge
```

Obviously, the modification would be discarded after package upgrade.
Use at your own risk.


## Testing

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
