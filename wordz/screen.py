import curses
import logging
from wordz.tracemore import get_exc_plus

logger = logging.getLogger('screen')


class Screen(object):
    _HIGHLIGHT = 7
    _ins = None

    def __new__(cls, stdscr=None, *a, **k):
        if cls._ins is None:
            _ins = super(Screen, cls).__new__(cls)
            if stdscr is None:
                stdscr = curses.initscr()

            curses.start_color()
            curses.use_default_colors()
            for i in range(0, curses.COLORS):
                curses.init_pair(i + 1, i, -1)

            curses.cbreak()
            stdscr.keypad(1)

            _ins.stdscr = stdscr
            _ins._closed = False
            _ins.handler = None

            cls._ins = _ins

        return cls._ins

    def close(self):
        if self._closed:
            return
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        self._closed = True

    __del__ = close

    def write(self, line, color=None):
        addstr = self.stdscr.addstr
        if color is not None:
            addstr(line, color)
        else:
            addstr(line)

    def handle(self, handler):
        self.handler = handler
        return self

    def __getattr__(self, item):
        return getattr(self.stdscr, item)

    def __enter__(self):
        if self.handler is None:
            raise RuntimeError('Usage: \nwith Screen().handle(handler) as f:\n'
                               '    f.getch()')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler(self.getch())
        self.handler = None
        if exc_type:
            logger.error(get_exc_plus())
        return True

    @property
    def height(self):
        return self.stdscr.getmaxyx()[0]

    @property
    def width(self):
        return self.stdscr.getmaxyx()[1]

    @property
    def HIGHLIGHT(self):
        return curses.color_pair(self._HIGHLIGHT)
