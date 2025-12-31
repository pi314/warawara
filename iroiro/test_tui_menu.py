from .lib_test_utils import *


class TestMenuData(TestCase):
    def test_basic(self):
        import iroiro
        data = iroiro.tui.MenuData()
        data['key'] = 'value'
        self.eq(data.key, 'value')

        data.key = 42
        self.eq(data['key'], 42)
        self.eq(repr(data), "MenuData({'key': 42})")

        del data.what
        self.eq(repr(data), "MenuData({'key': 42})")

        del data.key
        self.eq(repr(data), 'MenuData({})')

        data.key = 52
        self.eq(repr(data), "MenuData({'key': 52})")

        data.key = None
        self.eq(repr(data), 'MenuData({})')


class TestMenuCursor(TestCase):
    def setUp(self):
        import iroiro
        self.menu = iroiro.Menu('title', ['Option 1', 'Option 2', 'Option 3'])

    def test_repr(self):
        cursor = self.menu.cursor
        self.eq(repr(self.menu.cursor), f'MenuCursor(index={cursor.index}, wrap={cursor.wrap})')

    def test_str(self):
        self.eq(str(self.menu.cursor), '>')

    def test_add_sub_to(self):
        cursor = self.menu.cursor
        self.eq(cursor, 0)

        cursor += 1
        self.eq(cursor, 1)

        cursor += 1
        self.eq(cursor, 2)

        cursor += 10
        self.eq(cursor, 2)

        cursor -= 100
        self.eq(cursor, 0)

        cursor.to(1 + cursor)
        self.eq(cursor, 1)

        cursor.to(1 - cursor)
        self.eq(cursor, 0)

        cursor.to(1)
        self.ne(cursor, 0)
        self.gt(cursor, 0)
        self.ge(cursor, 0)
        self.ge(cursor, 1)
        self.eq(cursor, 1)
        self.le(cursor, 1)
        self.le(cursor, 2)
        self.lt(cursor, 2)
        self.ne(cursor, 2)

        cursor.up()
        self.eq(cursor, 0)

        cursor.down()
        cursor.down()
        self.eq(cursor, 2)

        cursor.to(self.menu[1])
        self.ne(cursor, self.menu[0])
        self.gt(cursor, self.menu[0])
        self.ge(cursor, self.menu[0])
        self.ge(cursor, self.menu[1])
        self.eq(cursor, self.menu[1])
        self.le(cursor, self.menu[1])
        self.le(cursor, self.menu[2])
        self.lt(cursor, self.menu[2])
        self.ne(cursor, self.menu[2])
        self.eq(cursor.text, 'Option 2')

    def test_up_down_wrap(self):
        cursor = self.menu.cursor

        cursor.wrap = True
        cursor.to(31)
        self.eq(cursor, 1)

        cursor.down()
        self.eq(cursor, 2)

        cursor.down()
        self.eq(cursor, 0)

        cursor.up()
        self.eq(cursor, 2)

    def test_to_diff_menu(self):
        import iroiro
        other_menu = iroiro.Menu('title', ['Option 1', 'Option 2', 'Option 3'])

        with self.raises(ValueError):
            self.menu.cursor.to(other_menu[1])

    def test_attr(self):
        cursor = self.menu.cursor

        cursor.to(1)
        self.eq(cursor.text, 'Option 2')

        with self.raises(AttributeError):
            cursor.bau

    def test_attr_relay(self):
        cursor = self.menu.cursor
        with self.raises(AttributeError):
            cursor.wrong_attr = 3

        cursor.to(self.menu[0])

        self.eq(cursor.text, self.menu[0].text)

        cursor.text = 'wah'
        self.eq(self.menu[0].text, 'wah')

        self.menu[0].text = 'iroiro'
        self.eq(cursor.text, 'iroiro')

    def test_relay_select_unselect_toggle(self):
        cursor = self.menu.cursor
        cursor.to(self.menu[0])

        cursor.select()
        self.true(self.menu[0].selected)

        cursor.unselect()
        self.false(self.menu[0].selected)

        cursor.toggle()
        self.true(self.menu[0].selected)

    def test_feedkey(self):
        cursor = self.menu.cursor
        cursor.to(self.menu[0])

        import queue
        q = queue.Queue()

        def foo(item, key):
            q.put((item, key))
            return 42
        self.menu[0].bind('k', foo)
        self.eq(cursor.feedkey('k'), 42)
        self.eq(q.get(), (self.menu[0], 'k'))


class TestMenuKeyHandler(TestCase):
    def setUp(self):
        import iroiro
        self.menu = iroiro.Menu('title', ['Option 1', 'Option 2'])

    def test_empty_handler(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(self.menu)
        ret = handler.handle('a')
        self.eq(ret, None)

    def test_bool(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(self.menu)
        print(handler.handlers)
        self.false(handler)
        handler.bind(lambda: None)
        self.true(handler)

    def test_bind_without_handler(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(self.menu)

        with self.raises(ValueError):
            handler.bind('a', 'b', 'c')

    def test_bind_with_wrong_signature(self):
        import iroiro

        handler = iroiro.tui.MenuKeyHandler(self.menu)
        with self.raises(iroiro.tui.MenuKeyHandler.SignatureError):
            handler.bind('k', lambda item, key: 'k')
        with self.raises(iroiro.tui.MenuKeyHandler.SignatureError):
            handler.bind('k', lambda hello, key: 'k')
        with self.raises(iroiro.tui.MenuKeyHandler.SignatureError):
            handler.bind('k', lambda key, hello: 'k')

        handler = iroiro.tui.MenuKeyHandler(self.menu[0])
        with self.raises(iroiro.tui.MenuKeyHandler.SignatureError):
            handler.bind('k', lambda menu, key: 'k')
        with self.raises(iroiro.tui.MenuKeyHandler.SignatureError):
            handler.bind('k', lambda hello, key: 'k')
        with self.raises(iroiro.tui.MenuKeyHandler.SignatureError):
            handler.bind('k', lambda key, hello: 'k')

    def test_bind_unbind_handler(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(self.menu)

        def foo(menu, key):
            pass

        def bar(menu, key):
            pass

        def baz(menu, key):
            pass

        handler.bind(foo, bar)
        self.eq(handler[None], [foo, bar])

        handler(baz)
        self.eq(handler[None], [foo, bar, baz])

        handler.unbind(foo, bar, baz)
        self.eq(handler[None], [])

        handler += foo
        self.eq(handler[None], [foo])
        handler += (bar, baz)
        self.eq(handler[None], [foo, bar, baz])

        handler -= bar
        self.eq(handler[None], [foo, baz])
        handler -= (baz, foo)
        self.eq(handler[None], [])

        handler['k'] += foo
        self.eq(handler['k'], [foo])
        handler['w'] += (bar, baz)
        self.eq(handler['w'], [bar, baz])

        handler['k'] = None
        self.eq(handler['k'], [])
        handler -= (baz, foo)
        self.eq(handler['k'], [])
        self.eq(handler['w'], [bar])
        handler['w'] -= [bar]
        self.eq(handler['w'], [])

        handler['k'] = None
        self.eq(handler['k'], [])

        handler['k'] = foo
        self.eq(handler['k'], [foo])
        handler['k'] = bar
        self.eq(handler['k'], [bar])
        handler -= 'k'
        self.eq(handler['k'], [])

    def test_ignore_duplicated_bind(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(self.menu)

        def foo(menu, key):
            by.append(foo)

        handler.bind(foo)
        handler.bind(foo)

        by = []
        ret = handler.handle('f')
        self.eq(by, [foo])

    def test_key_bubbling(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(self.menu)

        def foo(menu, key):
            by.append(foo)
            if key == 'f':
                return foo

        def bar(menu, key):
            by.append(bar)
            if key == 'r':
                return bar

        def baz(menu, key):
            by.append(baz)
            if key == 'z':
                return baz

        handler.bind(foo)

        handler.bind('b', bar)
        handler.bind('b', baz)

        handler.bind('f', bar)
        handler.bind('f', baz)

        handler.bind('r', bar)

        handler.bind('z', bar)
        handler.bind('z', baz)

        by = []
        ret = handler.handle('w')
        self.eq(ret, None)
        self.eq(by, [foo])

        by = []
        ret = handler.handle('b')
        self.eq(ret, None)
        self.eq(by, [bar, baz, foo])

        by = []
        ret = handler.handle('f')
        self.eq(ret, foo)
        self.eq(by, [bar, baz, foo])

        by = []
        ret = handler.handle('r')
        self.eq(ret, bar)
        self.eq(by, [bar])

        by = []
        ret = handler.handle('z')
        self.eq(ret, baz)
        self.eq(by, [bar, baz])

    def test_attach_to_menu_item(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(self.menu[0])

        by = []
        def foo(item, key):
            by.append(foo)
        handler += foo

        handler.handle('f')
        self.eq(by, [foo])

    def test_attach_to_something_else(self):
        import iroiro
        handler = iroiro.tui.MenuKeyHandler(iroiro)

        by = []
        def foo(key):
            by.append(foo)
            return key
        handler += foo

        ret = handler.handle('f')
        self.eq(ret, 'f')
        self.eq(by, [foo])

    def test_handler_flexible_signatures(self):
        import iroiro

        handler = iroiro.tui.MenuKeyHandler(self.menu)
        def empty():
            return 'e'
        handler += empty
        self.eq(handler.handle('k'), 'e')

        handler = iroiro.tui.MenuKeyHandler(self.menu)
        def key_only(key):
            return key
        handler += key_only
        self.eq(handler.handle('g'), 'g')

        handler = iroiro.tui.MenuKeyHandler(self.menu)
        def menu_only(menu):
            self.eq(menu, self.menu)
            return 'm'
        handler += menu_only
        self.eq(handler.handle('k'), 'm')

        handler = iroiro.tui.MenuKeyHandler(self.menu)
        def key_and_menu(key, menu):
            self.eq(menu, self.menu)
            return key
        handler += key_and_menu
        self.eq(handler.handle('%'), '%')

        handler = iroiro.tui.MenuKeyHandler(self.menu[0])
        def empty():
            return 'e'
        handler += empty
        self.eq(handler.handle('k'), 'e')

        handler = iroiro.tui.MenuKeyHandler(self.menu[0])
        def key_only(key):
            return key
        handler += key_only
        self.eq(handler.handle('k'), 'k')

        handler = iroiro.tui.MenuKeyHandler(self.menu[0])
        def item_only(item):
            self.eq(item, self.menu[0])
            return 'i'
        handler += item_only
        self.eq(handler.handle('k'), 'i')

        handler = iroiro.tui.MenuKeyHandler(self.menu[0])
        def key_and_item(key, item):
            self.eq(item, self.menu[0])
            return key
        handler += key_and_item
        self.eq(handler.handle('u'), 'u')


class TestMenuItem(TestCase):
    def setUp(self):
        import iroiro
        self.menu = iroiro.Menu('title', ['Option 1', 'Option 2', 'Option 3'])

    def test_repr(self):
        self.eq(repr(self.menu[0]), f"MenuItem(index=0, text='Option 1')")

    def test_index(self):
        for i in range(len(self.menu)):
            self.eq(self.menu[i].index, i)

    def test_select_unselect_toggle(self):
        i = self.menu[1]
        self.eq(i.selected, False)
        i.select()
        self.eq(i.selected, True)
        i.unselect()
        self.eq(i.selected, False)
        i.toggle()
        self.eq(i.selected, True)

    def test_moveto(self):
        i = self.menu[1]
        self.eq(i.index, 1)
        i.moveto(2)
        self.eq(i.index, 2)
        i.moveto(0)
        self.eq(i.index, 0)

    def test_cmp(self):
        self.eq(self.menu[0], 0)
        self.eq(self.menu[0], 'Option 1')
        self.ne(self.menu[0], None)

    def test_onkey(self):
        self.false(self.menu[0].onkey)

        self.menu[0].bind('a', lambda item, key: 'a')
        self.true(self.menu[0].onkey)

        self.menu[0].unbind('a')
        self.false(self.menu[0].onkey)

        self.menu[0].onkey = ('b', lambda item, key: 'b')
        self.true(self.menu[0].onkey)

        self.eq(self.menu[0].feedkey('a'), None)
        self.eq(self.menu[0].feedkey('b'), 'b')


class TestMenuThread(TestCase):
    def test_menu_thread(self):
        import iroiro
        menu = iroiro.Menu('title', ['Option 1', 'Option 2', 'Option 3'])

        checkpoint = self.checkpoint()

        def foo(*args, **kwargs):
            self.eq(args, (1, 2, 3))
            self.eq(kwargs, {'key': 'value'})
            checkpoint.wait()

        t = menu.Thread(target=foo, args=[1, 2, 3], kwargs={'key': 'value'})
        self.false(t.is_alive())

        t.start()
        self.true(t.thread.daemon)
        self.true(t.is_alive())
        checkpoint.set()

        t.join()
        self.false(t.is_alive())


class TestMenuStdoutNotTTY(TestCase):
    def test_menu_stdout_not_tty(self):
        import iroiro
        menu = iroiro.Menu('Do you like iroiro?', ['Yes', 'no'])
        with self.raises(iroiro.Menu.StdoutIsNotAtty):
            menu.interact()


class TestMenuFixture(TestCase):
    def setUp(self):
        from .lib_test_utils import FakeTerminal
        self.terminal = FakeTerminal()
        self.patch('sys.stdout.isatty', lambda *args, **kargs: True)
        self.patch('shutil.get_terminal_size', self.terminal.get_terminal_size)
        self.patch('iroiro.lib_tui.tui_print', lambda *args, **kwargs: self.terminal.print(*args, **kwargs))
        self.patch('iroiro.lib_tui.tui_flush', lambda: None)

        from contextlib import nullcontext
        self.patch('iroiro.lib_tui.HijackStdio', nullcontext)

        self.menu = None
        self.menu_ret = None

        import threading
        self.to_user = threading.Event()
        self.menu_thread = None

        import queue
        self.key_queue = queue.Queue()
        self.patch('iroiro.lib_tui.getch', self.mock_getch)

    def mock_getch(self, *args, **kwargs):
        self.to_user.set()
        ret = self.key_queue.get()
        return ret

    def start_menu(self, *args, **kwargs):
        def menu_runner(*args, **kwargs):
            try:
                self.menu_ret = self.menu.interact(*args, **kwargs)
            finally:
                self.to_user.set()

        import threading
        self.menu_thread = threading.Thread(target=menu_runner, args=args, kwargs=kwargs)
        self.menu_thread.daemon = True
        self.menu_thread.start()
        self.to_user.wait()

    def feedkey(self, key):
        self.to_user.clear()
        self.key_queue.put(key)
        self.to_user.wait()


class TestBasicMenu(TestMenuFixture):
    def test_menu_default_key_handlers(self):
        import iroiro

        self.menu = iroiro.Menu('Do you like iroiro?', ['Yes', 'no'])
        self.start_menu()
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> Yes',
            '  no',
            ])

        # Enter
        self.feedkey(iroiro.KEY_ENTER)
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> Yes',
            '  no',
            '',
            ])
        self.eq(self.menu.selected.text, 'Yes')

        self.terminal.reset()
        self.start_menu()
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> Yes',
            '  no',
            ])

        # q
        self.feedkey('q')
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> Yes',
            '  no',
            '',
            ])
        self.eq(self.menu.selected, None)

        self.terminal.reset()
        self.start_menu()
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> Yes',
            '  no',
            ])

        self.feedkey(iroiro.KEY_DOWN)
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  Yes',
            '> no',
            ])

        self.feedkey(iroiro.KEY_UP)
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> Yes',
            '  no',
            ])

        self.feedkey(iroiro.KEY_DOWN)
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  Yes',
            '> no',
            ])

        self.feedkey(iroiro.KEY_ENTER)
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  Yes',
            '> no',
            '',
            ])
        self.eq(self.menu.selected.text, 'no')


class TestSingleSelectMenu(TestMenuFixture):
    def test_menu_render(self):
        import iroiro
        self.menu = iroiro.Menu('Do you like iroiro?', ['Yes', 'no'], checkbox='()')
        self.start_menu()
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> ( ) Yes',
            '  ( ) no',
            ])

        self.feedkey(' ')
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> (*) Yes',
            '  ( ) no',
            ])

        self.feedkey(iroiro.KEY_DOWN)
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  (*) Yes',
            '> ( ) no',
            ])

        self.feedkey(' ')
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  ( ) Yes',
            '> (*) no',
            ])

        self.feedkey(' ')
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  ( ) Yes',
            '> ( ) no',
            ])


class TestMultiSelectMenu(TestMenuFixture):
    def test_menu_render(self):
        import iroiro
        self.menu = iroiro.Menu('Do you like iroiro?', ['Yes', 'no'], checkbox='[]')
        self.start_menu()
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> [ ] Yes',
            '  [ ] no',
            ])

        self.feedkey(' ')
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> [*] Yes',
            '  [ ] no',
            ])

        self.feedkey(iroiro.KEY_DOWN)
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  [*] Yes',
            '> [ ] no',
            ])

        self.feedkey(' ')
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '  [*] Yes',
            '> [*] no',
            ])

        self.feedkey(iroiro.KEY_UP)
        self.feedkey(' ')
        self.eq(self.terminal.lines, [
            'Do you like iroiro?',
            '> [ ] Yes',
            '  [*] no',
            ])
