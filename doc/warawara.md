# warawara

This is the index document of package `warawara`.


## Installation

```console
sh$ pip3 install warawara
```

Or just copy the whole folder to your machine, and add the path to `sys.path`:

```python
import sys
sys.path.insert(0, '/some/path/to/place/warawara')
import warawara
```


## Test

Testing:

```console
sh$ python3 -m unittest
```

With [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/):

```console
sh$ pipx install pytest-cov --include-deps
```

or

```console
sh$ pipx install pytest
sh$ pipx runpip pytest install pytest-cov

sh$ pytest --cov=warawara --cov-report=html
```


## "Attributes"

Like Python standard libraries, `warawara` divide its functionalities into
different categories.

For example, `warawara.subproc` contains functions about sub-processes,
`warawara.colors` contains fucntions about colors.

(Note that they are not sub-modules, so they are not `from warawara import xxx` able.)

For convenience, if not specified, functions are accessible directly at package level.
In other words, `warawara.subproc.xxx` is shortcut to `warawara.xxx`.

Documents and descriptions of the categories are as following:

*   [warawara](warawara.md)
*   [warawara.colors](warawara.colors.md)
*   [warawara.fs](warawara.fs.md)
*   [warawara.itertools](warawara.itertools.md)
*   [warawara.math](warawara.math.md)
*   [warawara.regex](warawara.regex.md)
*   [warawara.sh](warawara.sh.md)
*   [warawara.subproc](warawara.subproc.md)
*   [warawara.test_utils](warawara.test_utils.md)
*   [warawara.tui](warawara.tui.md)
