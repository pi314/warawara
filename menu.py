import sys
import os
import shutil


import smol


def main():
    if not sys.stdin.isatty():
        items = [line for line in sys.stdin]
    else:
        items = os.listdir('.')

    print(shutil.get_terminal_size())

    print(list(iter(smol.tui.MenuType)))

    def fmt(option):
        return option.name.lower()

    menu_type = smol.tui.menu('Select menu type:', options=smol.tui.MenuType, format=fmt, wrap=True)
    print(menu_type)
    print()

    def onkey(key, cursor):
        if key == '\x04':
            return 'DwD'

        if key == '\x01':
            return 'uwu'

        if key == 'tab':
            return 'twt'

        if key == 'space':
            return smol.tui.MenuOperation.TOGGLE

        if key == 'q':
            return

        if key == 'enter':
            if not cursor.selected:
                return smol.tui.MenuOperation.TOGGLE
            else:
                return smol.tui.MenuOperation.SELECT


    ret = smol.tui.menu('Select one you like:', options=items, type=menu_type, onkey=onkey, wrap=True)
    if isinstance(ret, tuple):
        print('You selected:', '(', ret[0], ')')
    elif isinstance(ret, list):
        print('You selected:', '[', ', '.join(ret), ']')
    else:
        print('You selected:', ret)


if __name__ == '__main__':
    main()
