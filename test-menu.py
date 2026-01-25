import sys
import time

import iroiro


def main():
    import os
    def format(menu, cursor, item, check, box):
        ind = ''
        if item.data.ind:
            ind = ' ' + item.data.ind

        if menu.data.grabbing and menu.cursor == item:
            return f'{cursor}{box[0]}{check}{box[1]} {item.text}{ind}'
        return f'{cursor} {box[0]}{check}{box[1]} {item.text}{ind}'
    menu = iroiro.Menu('title', ['unselectable', 'un-unselectable'] + iroiro.natsorted(os.listdir()), checkbox='[*]', format=format, max_height=20, message='', term_cursor_invisible=True)

    def pager_info(key):
        menu.message = 'key={} cursor={} grab={} text=[{}]\nvisible={} scroll={} height={}'.format(
                key, repr(menu.cursor), menu.data.grabbing, menu.cursor.text,
                menu.pager[int(menu.cursor)].visible, menu.pager.scroll, menu.pager.height)

    def onkey_vim(menu, key):
        if key == 'k':
            return menu.feedkey(iroiro.KEY_UP)
        elif key == 'j':
            return menu.feedkey(iroiro.KEY_DOWN)
        if key == 'h':
            return menu.feedkey(iroiro.KEY_LEFT)
        elif key == 'l':
            return menu.feedkey(iroiro.KEY_RIGHT)
        elif key == 'ctrl-y':
            menu.scroll(-1)
        elif key == 'ctrl-e':
            menu.scroll(1)
        elif key == 'g':
            menu.cursor = menu.first
        elif key == 'G':
            menu.cursor = menu.last
        elif key == 'H':
            menu.cursor = menu.top
        elif key == 'M':
            menu.cursor = (menu.top.index + menu.bottom.index) // 2
        elif key == 'L':
            menu.cursor = menu.bottom

        if menu.data.grabbing:
            menu.data.grabbing.moveto(menu.cursor)

        pager_info(key)

    def onkey_resize(menu, key):
        if key == '-':
            if not menu.pager.max_height:
                menu.pager.max_height = menu.pager.height - 1
            else:
                menu.pager.max_height -= 1
        elif key == '+':
            if not menu.pager.max_height:
                menu.pager.max_height = menu.pager.height + 1
            else:
                menu.pager.max_height += 1
        elif key == '=':
            menu.pager.max_height = None
        pager_info(key)

    def onkey(menu, key):
        unknown_key = False
        if key == 'w':
            menu.wrap = not menu.wrap
        elif key == 't':
            if menu.title == 'new title':
                menu.title = 'new multiline\ntitle'
            elif menu.title:
                menu.title = None
            else:
                menu.title = 'new title'
        elif key == 's':
            menu.message = 'scroll=' + str(menu.pager.scroll)
        else:
            unknown_key = True

        if not unknown_key:
            pager_info(key)
        else:
            menu.message = '[' + repr(key) + ']'

    def grab(menu, key):
        menu[menu.cursor].emit('grab')
    def ungrab(menu, key):
        menu[menu.cursor].emit('ungrab')
    def up(menu, key):
        menu.cursor.up()
        if menu.data.grabbing:
            menu.data.grabbing.moveto(menu.cursor)
    def down(menu, key):
        menu.cursor.down()
        if menu.data.grabbing:
            menu.data.grabbing.moveto(menu.cursor)
    menu.onkey(iroiro.KEY_UP, up)
    menu.onkey('down', down)
    menu.onkey(iroiro.KEY_LEFT, grab)
    menu.onkey(iroiro.KEY_RIGHT, ungrab)

    menu.onkey(onkey, onkey_vim, onkey_resize)
    menu.onkey('q', menu.quit)

    def index(menu, key):
        item = menu.cursor.item
        if key == 'i':
            menu.message = f'index={item.index}'
            return False
        elif key == 'space':
            item.toggle()

    def onselect(event, item):
        if not item.data.thread and not item.meta:
            def task():
                limit = 5
                item.data.start = time.time()
                while (time.time() - item.data.start) < limit:
                    item.data.ind = f'({int((limit + item.data.start - time.time()) * 1000) / 1000})'
                    time.sleep(0.0005)
                    item.menu.refresh()
                    if not menu.active:
                        break
                del item.data.thread
                del item.data.ind
                item.menu.refresh()
            item.data.thread = menu.Thread(target=task)
            item.data.thread.start()
        else:
            item.data.start = time.time()

    # for item in menu:
    #     item.onkey('i', 'space', index)
    menu.onkey(iroiro.KEY_SPACE, index)

    for item in menu:
        item.onselect = onselect

    def ongrab(item):
        menu.data.grabbing = menu[menu.cursor]
    def onungrab(item):
        if menu.data.grabbing is item:
            menu.data.grabbing = None
    menu.onevent('grab', ongrab)
    menu.onevent('ungrab', onungrab)

    def onquit(menu):
        menu.message = 'bye'
    menu.onquit = onquit

    menu[0].onselect(lambda event, item: False)
    menu[1].onunselect(lambda event, item: False)

    select_all = menu.append('Select all', meta=True)
    def check(*args, **kwargs):
        if all(item.selected for item in menu if not item.meta):
            return '*'
        elif all(not item.selected for item in menu if not item.meta):
            return ' '
        else:
            return '+'
    select_all.check = check
    def select_one_by_one(event, item):
        # item.menu.select_all()
        def task():
            import time
            for item in menu:
                if not item.meta:
                    item.select()
                    item.menu.refresh()
                    time.sleep(0.05)
            item.selected = True
        item.menu.Thread(target=task).start()
    # select_all.onkey(iroiro.KEY_SPACE, select_one_by_one)
    select_all.onselect = select_one_by_one

    unselect_all = menu.append('Unselect all', meta=True)
    def check(item):
        if all(item.selected for item in menu if not item.meta):
            return ' '
        elif all(not item.selected for item in menu if not item.meta):
            return '*'
        else:
            return '-'
    unselect_all.check = check
    unselect_all.onkey(iroiro.KEY_SPACE, menu.unselect_all)

    def enter(item, key):
        item.menu.message = 'enter'
        item.menu.submit()
    submit = menu.append('Submit', meta=True)
    def format_done(menu, cursor, item, check, box):
        if menu.data.grabbing and menu.cursor == item:
            return f'{cursor}{item.text}'
        return f'{cursor} {item.text}'
    submit.format = format_done
    submit.onkey(iroiro.KEY_ENTER, enter)

    def menu_enter(menu, key):
        # if menu.cursor.meta:
        #     return menu.cursor.feedkey(iroiro.KEY_SPACE)
        if menu.cursor.selected:
            menu.submit()
        else:
            menu.cursor.select()
    menu.onkey(iroiro.KEY_ENTER, menu_enter)

    i = 0
    def onsubmit(event, menu):
        if menu.data.grabbing:
            menu.data.grabbing.emit('ungrab')
            menu.message = 'try again'
            return False

        nonlocal i
        i += 1
        if i < 2:
            return False
    menu.onsubmit(onsubmit)

    ret = menu.interact()
    if isinstance(ret, list):
        for item in ret:
            print(item)
    else:
        print(ret)


if __name__ == '__main__':
    menu = iroiro.Menu('Do you like iroiro?', ['Yes', 'no'], checkbox='()')

    # ret = menu.interact()
    # print(ret)
    # if ret in (None, 'no'):
    #     sys.exit(1)
    #
    # print()
    # ret = menu.interact()
    # print(ret)
    # if ret in (None, 'no'):
    #     sys.exit(1)

    print()
    main()
