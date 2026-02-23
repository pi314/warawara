# iroiro

This is the index document of package `iroiro`.


## Installation

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


## "Attributes"

Like Python standard libraries, `iroiro` divide its functionalities into
different categories.

For example, `iroiro.subproc` contains functions about sub-processes,
`iroiro.colors` contains functions about colors.

(Note that they are not sub-modules, so they are not `from iroiro import xxx` able.)

For convenience, if not specified, functions are accessible directly at package level.
In other words, `iroiro.subproc.xxx` is shortcut-ed to `iroiro.xxx`.

Documents and descriptions of the categories are as following:

*   [iroiro](iroiro.md)
*   [iroiro.colors](iroiro.colors.md)
*   [iroiro.fs](iroiro.fs.md)
*   [iroiro.itertools](iroiro.itertools.md)
*   [iroiro.math](iroiro.math.md)
*   [iroiro.regex](iroiro.regex.md)
*   [iroiro.sh](iroiro.sh.md)
*   [iroiro.subproc](iroiro.subproc.md)
*   [iroiro.test_utils](iroiro.test_utils.md)
*   [iroiro.tui](iroiro.tui.md)
