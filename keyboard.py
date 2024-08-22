import smol


def main():
    ret = smol.tui.menu('Select one you like:', options=['apple', 'bana', 'banana', '水果'], wrap=True)
    print('You selected:', ret)


if __name__ == '__main__':
    main()
