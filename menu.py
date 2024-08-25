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

    def onkey(key, cursor):
        if key == '\x04':
            return 'DwD'

        if key == '\x01':
            return 'uwu'

        if key == 'tab':
            return 'twt'

        if key == 'space':
            return 'toggle'

        if key == 'q':
            return

        if key == 'enter':
            if not cursor.selected:
                return 'toggle'
            else:
                return 'select'


    ret = smol.tui.menu('Select one you like:', options=items, type='checkbox', onkey=onkey, wrap=True)
    if isinstance(ret, tuple):
        print('You selected:', '(', ret[0].text, ')')
    elif isinstance(ret, list):
        print('You selected:', '[', ', '.join([opt.text for opt in ret]), ']')
    else:
        print('You selected:', ret.text)


if __name__ == '__main__':
    main()
