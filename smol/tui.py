import itertools
import threading
import time


__all__ = ['ThreadedSpinner']


class ThreadedSpinner:
    def __init__(self, *icon, delay=0.1):
        if not icon:
            self.icon_entry = '⠉⠛⠿⣿⠿⠛⠉⠙'
            self.icon_loop = '⠹⢸⣰⣤⣆⡇⠏⠛'
            self.icon_leave = '⣿'
        elif isinstance(icon, str):
            self.icon_entry = tuple()
            self.icon_loop = [icon]
            self.icon_leave = tuple()
        elif len(icon) == 1:
            self.icon_entry = tuple()
            self.icon_loop = icon
            self.icon_leave = tuple()
        elif len(icon) == 2:
            self.icon_entry = icon[0]
            self.icon_loop = icon[1]
            self.icon_leave = tuple()
        elif len(icon) == 3:
            self.icon_entry = icon[0]
            self.icon_loop = icon[1]
            self.icon_leave = icon[2]
        else:
            raise ValueError('Invalid value: ' + repr(icon))

        self.delay = delay
        self.end = False
        self.thread = None
        self.index = 0
        self._text = ''
        self.icon_iter = (
                itertools.chain(
                    self.icon_entry,
                    itertools.cycle(self.icon_loop)
                    ),
                iter(self.icon_leave)
                )
        self.icon_head = [
                next(self.icon_iter[0]),
                next(self.icon_iter[1])
                ]

    def __enter__(self):
        if self.thread:
            return self

        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.join()

    @property
    def icon(self):
        return self.icon_head[self.end]

    def text(self, *args):
        if not args:
            return self._text

        self._text = ' '.join(str(a) for a in args)
        self.refresh()

    def refresh(self):
        print('\r' + self.icon + '\033[K ' + self._text, end='')

    def animate(self):
        self.index = 0
        while not self.end:
            self.refresh()
            time.sleep(self.delay)
            self.icon_head[0] = next(self.icon_iter[0])

        try:
            while True:
                self.refresh()
                time.sleep(self.delay)
                self.icon_head[1] = next(self.icon_iter[1])
        except StopIteration:
            pass

        print()

    def start(self):
        if self.thread:
            return

        self.thread = threading.Thread(target=self.animate)
        self.thread.daemon = True
        self.thread.start()

    def join(self):
        self.end = True
        self.thread.join()
