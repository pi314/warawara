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

    # def fmt(option):
    #     return option.name.lower()

    menu_type = smol.tui.menu('Select menu type:', options=map(lambda x: x.name.lower(), smol.tui.MenuType), wrap=True)
    print(menu_type)
    print()

    if menu_type is None:
        return

    def onkey(menu, cursor, key):
        if key == '\x04':
            menu.message = 'DwD'
            return False

        if key == '\x01':
            menu.message = 'uwu'
            return False

        if key == 'tab':
            menu.message = 'uwu'
            return False

        if key == 'space':
            if menu[cursor].text == 'select all':
                menu.select_all()
                return False
            elif menu[cursor].text == 'unselect all':
                menu.unselect_all()
                return False
            else:
                menu.toggle()
                return False

        if key == 'enter':
            if not menu[cursor].selected:
                menu.toggle()
            else:
                return menu

            return False

        if key == 'c':
            menu.unselect_all()
            return False

        if key == 'a':
            menu.select_all()
            return False

    ret = smol.tui.menu('Select one you like:', options=['select all', 'unselect all'] + items, type=menu_type, onkey=onkey, wrap=True)
    if isinstance(ret, tuple):
        print('You selected:', '(', ret[0], ')')
    elif isinstance(ret, list):
        print('You selected:', '[', ', '.join(ret), ']')
    else:
        print('You selected:', ret)


if __name__ == '__main__':
    main()
