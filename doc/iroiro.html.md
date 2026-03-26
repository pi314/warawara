# iroiro.regex

This document describes the API set provided by `iroiro.html`.

For the index of this package, see [iroiro.md](iroiro.md).


## Class `HTML`

A class that parses and build tree from given HTML.

__Parameters__
```python
HTML(source, keep_comments=False, pre='pre')
```

*   `source`
    -   `pathlib.Path`: `source` is opened and read.
    -   `file`: data is read through `source.read()`.
    -   `str`: `source` is taken as html string.

*   `keep_comments`: drop comments if `False`.

*   `pre`: a set of tags. Inside these tags, white spaces and newlines are reserved.


__Examples__
```python
import pathlib
import iroiro
path = pathlib.Path(...)

doc = iroiro.HTML(p, keep_comments=True, pre={'span', 'div'})
```
