# menu
# menu[n]
# menu.cursor
#
# menu.prompt
# menu.arrow
# ?x menu.onkey
# ? menu.onkey(func[menu, key])
# ? menu.onkey(key, func[menu])
# menu.message
# ?menu.color
#
# ?x menu[n].onkey = func
# ? menu[n].onkey(func[item, key])
# ? menu[n].onkey(key, func[item])
# menu[n].text
# menu[n].arrow
# menu[n].mark
# menu[n].select()
# menu[n].unselect()
# menu[n].color
#
# menu.cursor
# menu.cursor.select()
# menu.cursor.unselect()
# menu.cursor.color




import sys
import os
import shutil


import smol

smol.register_key(chr(ord('u') - ord('a') + 1), 'uwu')
smol.register_key(chr(ord('w') - ord('a') + 1), 'wuw')


def main():
    if not sys.stdin.isatty():
        items = [line for line in sys.stdin]
    else:
        items = os.listdir('.')

    items.sort()

    print(shutil.get_terminal_size())

    def vim_key(who, key):
        if key == 'j':
            return 'down'
        if key == 'k':
            return 'up'
        if key == 'H':
            return 'home'
        if key == 'L':
            return 'end'
        if key in ('0', '^'):
            return 'home'
        if key in ('G', '$'):
            return 'end'

    def vim_scroll(who, key):
        if key == 'y':
            return 'up'
        if key == 'e':
            return 'down'

    def onkey(menu, key):
        if key == 'd':
            menu.cursor = 'default'
        elif key == 'r':
            menu.cursor = 'radio'
        elif key == 'c':
            menu.cursor = 'checkbox'

    menu = smol.tui.Menu('Select menu type:', options=['default', 'radio', 'checkbox'], onkey=[vim_key, onkey], wrap=True)
    # menu.bind(onkey)
    menu_type = menu.interact()
    print(menu_type)
    print()

    if menu_type is None:
        return

    def onkey(menu, key):
        if key == '\x04':
            menu.message = 'DwD'
            return False

        if key == '\x01':
            menu.message = 'AwA'
            return False

        if key == 'uwu':
            menu.message = 'UwU'
            return False

        if key == 'wuw':
            menu.message = 'WuW'
            return False

        if key == 'tab':
            menu.message = 'TwT'
            return False

        if key == 'enter':
            if not menu.type:
                return None

            if menu.cursor == -1:
                menu.done()
            else:
                return False

            return False

        if key == 'c':
            menu.unselect_all()
            return False

        if key == 'a':
            menu.select_all()
            return False

        if key == 'd':
            menu.cursor = 'Done'

    if menu_type == 'checkbox':
        phony_options = ['Select all', 'Unselect all'] + items + ['Done']
    else:
        phony_options = items

    menu = smol.tui.Menu('Select one you like:', options=phony_options, type=menu_type, onkey=None, wrap=True)
    menu.bind(vim_key)
    menu.bind([vim_scroll, onkey])

    if menu_type == 'checkbox':
        menu[0].phony = True
        menu[0].mark = lambda item: {
                len(items): '*',
                0: ' '
                }.get(sum(i.selected for i in item.menu if not i.phony), '-')
        def select_all_onkey(item, key):
            item.menu.select_all()
            item.menu.cursor.color = smol.black / smol.green
            return False
        menu[0].bind('space', select_all_onkey)

        def unselect_all_onkey(item, key):
            item.menu.unselect_all()
            item.menu.cursor.color = smol.black / smol.red
            return False
        menu[1].phony = True
        menu[1].mark = lambda item: {
                len(items): ' ',
                0: '*'
                }.get(sum(i.selected for i in item.menu if not i.phony), '-')
        menu[1].bind('space', unselect_all_onkey)

        menu[-1].phony = True
        menu[-1].mark = lambda item: '>' if item.focused else ' '
        menu[-1].arrow = ' '
        def done_onkey(item, key):
            if key == 'space':
                item.menu.cursor.color = smol.black / smol.white
                if not item.checkbox or item.checkbox == '{}':
                    item.checkbox = '()'
                else:
                    item.checkbox = '{}'
                return False
            if key == 'enter':
                item.menu.done()
        menu[-1].bind(done_onkey)

    ret = menu.interact()
    if isinstance(ret, tuple):
        print('You selected:', repr(ret))
    elif isinstance(ret, list):
        print('You selected:', repr(ret))
    else:
        print('You selected:', ret)


if __name__ == '__main__':
    main()
