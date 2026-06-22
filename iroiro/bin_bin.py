import os
import sys
import argparse
import shutil

from pathlib import Path

from .lib_colors import lime, murasaki, teal
from .lib_tui import strwidth, ljust
from .lib_tui import Menu, KEY_UP, KEY_DOWN, KEY_SPACE, KEY_ENTER


BIN_PATH = Path(__file__).parent / 'bin'
BIN_DISABLED_PATH = BIN_PATH / 'disabled'


def collect_util_list():
    def _util_list(path):
        ret = []
        try:
            for n in os.listdir(path):
                p = path / n
                if not p.is_file() or p.suffix:
                    continue
                ret.append(n)
        except:
            pass
        return ret

    ret = []
    ret.extend(_util_list(BIN_PATH))
    ret.extend(_util_list(BIN_DISABLED_PATH))

    return sorted(ret)


def get_util_status(util):
    if util not in collect_util_list():
        return

    util_epath = BIN_PATH / util
    util_dpath = BIN_DISABLED_PATH / util
    if util_epath.exists():
        return True
    if util_dpath.exists():
        return False


def set_util_status(util, status):
    if util not in collect_util_list():
        return

    util_epath = BIN_PATH / util
    util_dpath = BIN_DISABLED_PATH / util
    try:
        if status:
            if not util_epath.exists() and util_dpath.exists():
                util_dpath.rename(util_epath)
        else:
            if not BIN_DISABLED_PATH.exists():
                BIN_DISABLED_PATH.mkdir(parents=True, exist_ok=True)

            if util_epath.exists():
                if util_dpath.exists():
                    util_dpath.unlink()
                util_epath.rename(util_dpath)
        return True
    except:
        return False


def toggle_util_status(util):
    if util not in collect_util_list():
        return
    status = get_util_status(util)
    return set_util_status(util, not status)


def usage():
    print('Usage:')
    PS1 = murasaki('$')
    print(PS1, 'iroiro bin', teal('# interactive mode'))
    print(PS1, 'iroiro bin list')
    print(PS1, 'iroiro bin enable util [util ...]')
    print(PS1, 'iroiro bin disable util [util ...]')
    sys.exit(1)


def main():
    prog = sys.argv[0]
    argv = sys.argv[1:]

    if '-h' in argv or '--help' in argv:
        usage()

    op = 'manage'
    if argv and argv[0] in ('list', 'enable', 'disable'):
        op = argv[0]
        argv.pop(0)

    util_list = collect_util_list()

    if op == 'list':
        ind = {util: lime('enabled')
               if get_util_status(util)
               else murasaki('disabled')
               for util in util_list}
        width = max(strwidth(ind[util]) for util in util_list)
        for util in util_list:
            print(ljust(ind[util], width), '│', util)

    if op == 'enable':
        res = True
        for arg in argv:
            res = res and set_util_status(arg, True)
        sys.exit(0 if res else 1)

    if op == 'disable':
        res = True
        for arg in argv:
            res = res and set_util_status(arg, False)
        sys.exit(0 if res else 1)

    if op == 'manage':
        def format(menu, cursor, item, check, box):
            item_color = lime if get_util_status(item.text) else murasaki
            check = item_color('enabled ' if item.selected else 'disabled')
            sep = '-' if item.data.thread else '│'
            return f'{cursor} {check} {sep} {item.text}'

        menu = Menu(util_list, checkbox='[]', format=format,
                    message=None,
                    max_height=20, term_cursor_invisible=True)

        def onkey_vim(menu, key):
            if key == 'k':
                return menu.feedkey(KEY_UP)
            elif key == 'j':
                return menu.feedkey(KEY_DOWN)
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

        menu.onkey(KEY_UP, menu.cursor.up)
        menu.onkey(KEY_DOWN, menu.cursor.down)
        menu.onkey(KEY_SPACE, menu.cursor.toggle)
        menu.onkey(KEY_ENTER, menu.cursor.select)
        menu.onkey('q', menu.quit)
        menu.onkey += onkey_vim

        def onselect(event, item):
            if not item.data.thread:
                def task():
                    toggle_util_status(item.text)
                    del item.data.thread
                    item.menu.refresh(force=True)
                item.data.thread = menu.Thread(target=task)
                item.data.thread.start()
            return True

        for idx, util in enumerate(util_list):
            menu[idx].selected = get_util_status(util)
            menu[idx].onselect = onselect
            menu[idx].onunselect = onselect

        menu.interact()
        menu.threads.join()
