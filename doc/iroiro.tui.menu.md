# iroiro.tui.menu

This document describes Menu-related API provided by [`iroiro.tui`](iroiro.tui.md).

For the index of this package, see [iroiro.md](iroiro.md).


## Class `Menu`

`Menu` provides a configurable, non-ncurses, interactive menu.

For example:

```console
Do you like iroiro?
> Yes
  Absolutelly yes
```

User could use `q` or `ctrl+c` to abort the selection, arrow keys to move cursor, and `enter` to select.


__Parameters__
```python
Menu(title=None, options=None, *,
     message=None, max_height=None,
     wrap=False, format=None, cursor='>', checkbox=None,
     onkey=None, term_cursor_invisible=None)
```

*   `title`
    -   The text that stays on top of the menu.

*   `options`
    -   Options, should be in `str`.

*   `message`
    -   The text than stays on the bottom of the menu.

*   `max_height`
    -   Height limitation.
    -   By default iroiro query terminal height and width.

*   `wrap`
    -   If set to `True`, cursor wrap around first and last options.
    -   Press `down` on the last item moves cursor to the first one.
    -   Prexx `up` on the first item moves cursor to the last one.

*   `format`
    -   Defines the display format when rendering items.
