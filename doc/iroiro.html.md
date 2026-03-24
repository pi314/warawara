# iroiro.regex

This document describes the API set provided by `iroiro.html`.

For the index of this package, see [iroiro.md](iroiro.md).


## Class `HTML`

A class that parses and build tree from given HTML.

__Parameters__
```python
HTML(source, keep_comments=False, pre='pre')
```

*   `source`: `str` or `file`

*   `keep_comments`: drop comments if `False`.

*   `pre`: a set of tags. Inside these tags, white spaces and newlines are reserd.
