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

    menu = smol.tui.Menu('Select menu type:', options=map(lambda x: x.name.lower(), smol.tui.MenuType), wrap=True)
    menu_type = menu.interact()
    print(menu_type)
    print()

    if menu_type is None:
        return

    def onkey(menu, cursor, key):
        if key == '\x04':
            menu.message = 'DwD'
            return False

        if key == '\x01':
            menu.message = 'AwA'
            return False

        if key == chr(ord('u') - ord('a') + 1):
            menu.message = 'UwU'
            return False

        if key == 'tab':
            menu.message = 'TwT'
            return False

        if key == 'space':
            if menu[cursor].text == 'select all':
                menu.select_all()
                menu[1].unselect()
                return False
            elif menu[cursor].text == 'unselect all':
                menu.unselect_all()
                return False
            else:
                menu[cursor].toggle()
                return False

        if key == 'enter':
            if not menu.type:
                return None
            if not menu[cursor].selected:
                menu[cursor].select()
            else:
                menu.done()

            return False

        if key == 'c':
            menu.unselect_all()
            return False

        if key == 'a':
            menu.select_all()
            return False

    menu = smol.tui.Menu('Select one you like:', options=['select all', 'unselect all'] + items, type=menu_type, onkey=onkey, wrap=True)
    ret = menu.interact()
    if isinstance(ret, tuple):
        print('You selected:', '(', ret[0], ')')
    elif isinstance(ret, list):
        print('You selected:', '[', ', '.join(ret), ']')
    else:
        print('You selected:', ret)


if __name__ == '__main__':
    main()
