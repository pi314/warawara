import sys
import os
import shutil


import smol


def main():
    if not sys.stdin.isatty():
        items = [line for line in sys.stdin]
    else:
        items = os.listdir('.')

    items.sort()

    print(shutil.get_terminal_size())

    def onkey(menu, cursor, key):
        if key == 'd':
            menu.cursor_move('default')
        elif key == 'r':
            menu.cursor_move('radio')
        elif key == 'c':
            menu.cursor_move('checkbox')

    menu = smol.tui.Menu('Select menu type:', options=['default', 'radio', 'checkbox'], onkey=onkey, wrap=True)
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

    meta_options = ['Select all', 'Unselect all', 'Done'] if menu_type == 'checkbox' else []
    menu = smol.tui.Menu('Select one you like:', options=meta_options[:2] + items + [meta_options[-1]], type=menu_type, onkey=onkey, wrap=True)
    if meta_options:
        menu[0].set_meta(mark=lambda menu: '*' if all(item.selected for item in menu[2:-1]) else '-' if any(item.selected for item in menu[2:-1]) else ' ')
        def select_all_onkey(menu, cursor, key):
            if key == 'space':
                menu.select_all()
                return False
        menu[0].onkey = select_all_onkey

        def unselect_all_onkey(menu, cursor, key):
            if key == 'space':
                menu.unselect_all()
                return False
        menu[1].set_meta(
                mark=lambda menu: ' ' if all(item.selected for item in menu[2:-1]) else '-' if any(item.selected for item in menu[2:-1]) else '*',
                onkey=unselect_all_onkey)

        menu[-1].set_meta(mark=lambda menu: '>' if menu.index == len(menu) - 1 else ' ')
        menu[-1].cursor = ' '
        def done_onkey(menu, cursor, key):
            if key == 'enter':
                menu.done()
        menu[-1].onkey = done_onkey

    ret = menu.interact()
    if isinstance(ret, tuple):
        print('You selected:', '(', ret[0], ')')
    elif isinstance(ret, list):
        print('You selected:', '[', ', '.join(ret), ']')
    else:
        print('You selected:', ret)


if __name__ == '__main__':
    main()
