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

Multi-select menu:

```
Do you like iroiro?
> [*] Yes
  [*] Absolutelly yes
```

`q` and `ctrl+c` abort the selection, `up` and `down` move cursor,
`space` selects/toggles item, and `enter` finalizes the result.

Each of items in menu is in `MenuItem`, see its description below.


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
        +   `'{cursor} {box[0]}{check}{box[1]} {item.text}'` for single and multi- select menu
    -   Otherwise, `str.format()` is used as the formatting entry point
    -   The following arguments are passed to the formatter:
        +   `menu`: the menu object
        +   `cursor`: the cursor string or space, padded to the same display width
        +   `item`: the item being formatted
        +   `check`: the check mark or space, padded to the same display width
        +   `box`: the checkbox that wraps checkmark,
            `box[0]` and `box[1]` being the left part and right part, respectively

*   `checkbox`: type of the menu
    -   `()`: single select menu, with checkmark `*`
    -   `(...)`: single select menu, with customized checkmark
    -   `[]`: multi-select menu, with checkmark `*`
    -   `(...)`: multi-select menu, with customized checkmark
    -   Otherwise, recognized as basic menu
    -   If you want more precised control on checkmark and box characters,
        set this parameter to `()` or `[]` and use `format` for rendering

*   `onkey`: TBA

*   `term_cursor_invisible`: whether to set cursor as invisible during interaction
    -   `True`: hide cursor
    -   `False`: show cursor at the last line on each cycle
    -   `None`: `bool(message is None)`


### Methods and Properties

#### `Menu.interact()`
Starts the menu interaction loop, and returns the select items after interaction ends.

__Parameters__
```python
Menu.interact(suppress=(EOFError, KeyboardInterrupt, BlockingIOError))
```

If an exception listed in `suppress` happens, the funciton returns `None`.

__Examples__
```python
menu = Menu(...)
res = menu.interact()
print(res)
```

The selected item(s) could also be accessed through `Menu.selected` .


#### Property `Menu.selected`
*   For single selected menu, it's the selected `MenuItem` or `None`.
*   For multi-select menu, it's a `[MenuItem]` of selected items (or `[]`.)
*   For basic menu, it's the selected `MenuItem` or `None`.

It's dynamically calculated every time when accessed.


#### `Menu.__getitem__(idx)`
`Menu[idx]` returns the `MenuItem` object at index `idx`.


#### `Menu.__setitem__(idx, value)`
Sets `Menu[idx].text` to `str(value)`


## Class `MenuItem`
`MenuItem` has the following methods and attributes
