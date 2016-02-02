import textwrap
import curses
import logging
from wordz import keys

logger = logging.getLogger('single_select')


class SingleSelect(object):
    check = '\u2713'

    def __init__(self, content, current=0, default=0, padding=0, lineno=False):
        self.content = content
        self.current = current
        self.select = default
        self.padding = padding
        self.lineno = lineno

    def render(self, screen):
        width = screen.width - self.padding
        for index, raw_content in enumerate(self.content):

            color = screen.HIGHLIGHT if index == self.current else None
            if self.lineno:
                lineno = ' %s.' % (index + 1)
            else:
                lineno = ''
            prefix = (' ' * self.padding) + ('%s%s ' % (self.check if color else ' ', lineno))
            _, old_x = screen.getyx()
            screen.write(prefix, color)
            _, new_x = screen.getyx()
            indent = ' ' * new_x

            for each_ch in raw_content:
                screen.write(each_ch, color)
                if each_ch == '\n':
                    screen.write(indent, color)
                else:
                    _, now_x = screen.getyx()
                    if now_x >= width - 1:
                        screen.write('\n' + indent, color)
            else:
                screen.write('\n')

    def handler(self, k):
        # if k in (keys.KEY_ENTER, keys.KEY_SPACE):
        #     self.select = self.current
        #     return

        if k == keys.KEY_UP:
            offset = -1
        elif k == keys.KEY_DOWN:
            offset = 1
        else:
            allowed = len(self.content)
            for each in ('A', 'a', '1'):
                asc_num = ord(each)
                index = k - asc_num
                if 0 <= index < allowed:
                    break
            else:
                return False
            
            self.select = self.current = index
            return True

        max_num = len(self.content) - 1

        current = self.current + offset
        if current < 0:
            current = max_num

        elif current > max_num:
            current = 0

        self.current = self.select = current
        return False

    def get_selected(self):
        return self.select


    def select_item(self, index):
        self.select = index

    def get(self):
        return self.select


def main(stdscr): 
    import string
    import sys
    import atexit
    ss = SingleSelect([('中文%s' % x) * 20 for x in range(4)], padding=5, lineno=True)
    # ss = SingleSelect('ABCD', [(string.ascii_letters) * 4 for x in range(4)])
    screen = Screen(stdscr)
    atexit.register(lambda: sys.__stdout__.write('select %s' % ss.select))
    while True:
        with screen.handle(ss.handler) as s:
            s.clear()
            ss.render(s)


if __name__ == '__main__':
    from wordz.screen import Screen
    from wordz.bashlog import filelogger, stdoutlogger, DEBUG
    from wordz.main import redirect
    stdoutlogger(None, DEBUG)
    redirect()
    # filelogger('/tmp/wordz.log', None, DEBUG)
    curses.wrapper(main)
