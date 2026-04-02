# iroiro.tui.menu

This document describes Menu-related API provided by [`iroiro.tui`](iroiro.tui.md).

For the index of this package, see [iroiro.md](iroiro.md).


## Overview
All menu related features are provided through `Menu` class and/or its attributes.

While some of the features are described using internal class/function name in this document,
they are not intented for being used directly.

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


## Class `Menu`

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
Given `menu` referencing to a `Menu` instance,

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

The selected item(s) could also be accessed through `menu.selected` .


#### Property `Menu.selected`
*   For basic and single select menu, it's the selected `MenuItem` or `None`.
*   For multi-select menu, it's a `[MenuItem]` of selected items (or `[]`.)

It's dynamically calculated every time when accessed.


#### Menu item

`menu[n]` access to n-th item

*   `menu[n].text` is the displayed text

*   `menu[n].selected` indicates whether the item is selected

*   `menu[n].select()`/`unselect()`/`toggle()` switch selection status of the item

*   `menu[n] = value` sets `menu[n].text` to `str(value)`

*   `menu[n].check` returns check mark of the item

    -   Could be used for `format`ing

*   `menu[n].box` returns checkbox of the item

    -   Could be used for `format`ing

*   `menu[n].index` returns `n`

*   `menu[n].moveto(where)` moves the item to `where`

    -   It's not swapping, it slides through the adjacent items


#### Menu cursor

`menu.cursor` access to menu cursor

*   `menu.cursor.pos` is the cursor position

    -   Also `int(menu.cursor)` and `menu.cursor.index`

*   `str(menu.cursor)` returns the cursor symbol

*   `menu.cursor.item` points to the actual item object

*   `menu.cursor.up()`/`down()` moves cursor up/down

*   `menu.cursor` `-=1`/`+=1` also moves cursor up/down

*   `menu.cursor.to(N)` moves cursor to `N`-th item

*   `menu.cursor.select()`/`unselect()`/`toggle()` switch selection status of the pointed item


#### Menu Key Handler

`menu.onkey(key, handler)` binds `handler` to `key` ([`MenuKeyHandler`](#class-menukeyhandler)),
i.e. when `key` is pressed, `handler` is called.

`menu.onkey[key](handler)` does the same.


#### Menu Event Handler

`.onselect` / `.onunselect` / `.onsubmit` / `.onquit`

`onevent('myevent', handler)`
