# iroiro.tui.menu

This document describes Menu-related API provided by [`iroiro.tui`](iroiro.tui.md).

For the index of this package, see [iroiro.md](iroiro.md).


## Class `Menu`

`Menu` provides a configurable, interactive, non-ncurses menu.

Basic menu:

```
Do you like iroiro?
> Yes
  Absolutelly yes
```

Single select (radio) menu:

```
Do you like iroiro?
> (*) Yes
  ( ) Absolutelly yes
```

Multiple select menu:

```
Do you like iroiro?
> [*] Yes
  [*] Absolutelly yes
```

`q` and `ctrl+c` abort the selection, `up` and `down` move cursor,
`space` selects/toggles item, and `enter` finalizes the result.


__Parameters__
```python
Menu(title=None, options=None, *,
     message=None, max_height=None,
     wrap=False, format=None, cursor='>', checkbox=None,
     onkey=None, term_cursor_invisible=None)
```

*   `title`: the text that stays at top of the menu

*   `options`: options in `list[str]`

*   `message`: the text that stays at the bottom of the menu

*   `max_height`: limitation of menu height
    -   By default iroiro queries terminal height and width

*   `wrap`: whether to wrap cursor around first and last options
    -   Press `down` on the last item moves cursor to the first one
    -   Press `up` on the first item moves cursor to the last one

*   `format`: the display format for rendering items
    -   If a `callable` is specified, it's used as the formatting entry point
    -   If it's `None`, the default value is decided by menu type
        +   `'{cursor} {item.text}'` for basic menu
        +   `'{cursor} {box[0]}{check}{box[1]} {item.text}'` for single and multiple select menu
    -   Otherwise, `str.format()` is used as the formatting entry point
    -   The following arguments are passed to the formatter:
        +   `menu`: the menu object
        +   `cursor`: the cursor string or space, padded to the same display width
        +   `item`: the item being formatted
        +   `check`: the check mark or space, padded to the same display width
        +   `box`: the checkbox that wraps checkmark,
            `box[0]` and `box[1]` being the left part and right part, respectively
