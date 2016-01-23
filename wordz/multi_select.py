import textwrap
import curses
import logging
from wordz import keys

logger = logging.getLogger('single_select')


class MultiSelect(object):
    check = '\u2713'

    def __init__(self, content, current=0, default=None, padding=0, lineno=False):
        self.content = content
        self.current = 0
        self.select = set(default or ())
        self.selected = False
        self.padding = padding
        self.lineno = lineno

    def render(self, screen):
        width = screen.width - self.padding

        for index, raw_content in enumerate(self.content):
            color = screen.HIGHLIGHT if index == self.current else None
            checked = index in self.select

            if self.lineno:
                lineno = '%s. ' % (index + 1)
            else:
                lineno = ''

            prefix = (' ' * self.padding) + '[%s]%s' % (self.check if checked else ' ', lineno)

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
        if k == keys.KEY_ENTER:
            self.selected = True
            return

        if k == keys.KEY_SPACE:
            current = self.current
            selected = self.select
            if current in selected:
                selected.remove(current)
            else:
                selected.add(current)
            return

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
                return
            
            self.current = index

            selected = self.select
            if index in selected:
                selected.remove(index)
            else:
                selected.add(index)
            return

        max_num = len(self.content) - 1

        current = self.current + offset
        if current < 0:
            current = max_num

        elif current > max_num:
            current = 0

        self.current = current

    def get_selected(self):
        if not self.selected:
            return None
        return self.select



def main(stdscr): 
    # import string
    ms = MultiSelect([('中文%s' % x) * 20 for x in range(4)], padding=5, default=[0, 3], lineno=True)
    # ss = SingleSelect('ABCD', [(string.ascii_letters) * 4 for x in range(4)])
    screen = Screen(stdscr)
    while ms.get_selected() is None:
        with screen.handle(ms.handler) as s:
            s.clear()
            ms.render(s)
    else:
        print(ms.get_selected())


if __name__ == '__main__':
    from wordz.screen import Screen
    from wordz.bashlog import filelogger, stdoutlogger, DEBUG
    from wordz.main import redirect
    redirect()
    stdoutlogger(None, DEBUG)
    # filelogger('/tmp/wordz.log', None, DEBUG)
    curses.wrapper(main)

