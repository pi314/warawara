import sys


import smol


def main():
    if not sys.stdin.isatty():
        items = [line for line in sys.stdin]
    else:
        items = ['Default item 1', 'Default item 2', 'Defaaaaaauuuuulllltttt item 33333']

    def onkey(key, cursor):
        if key == '\x04':
            return 'DwD'

        if key == '\x01':
            return 'uwu'

        if key == 'tab':
            return 'twt'

        if key == 'space':
            return ''

        return key


    ret = smol.tui.menu('Select one you like:', options=items, onkey=onkey, wrap=True)
    print('You selected:', ret)


if __name__ == '__main__':
    main()
