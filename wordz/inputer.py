import curses
import logging
from wordz import keys

logger = logging.getLogger('inputer')


class Inputer(object):

    def __init__(self, placeholder='', padding=0):
        self.inputted = []
        self.placeholder = placeholder
        self.padding = padding

    def render(self, screen):
        padding = ' ' * self.padding
        screen.write(padding)
        if self.inputted:
            screen.write(''.join(self.inputted))
            screen.write('I', self.place_color)
        else:
            screen.write(self.placeholder, self.place_color)

    def handler(self, k):
        if k in (keys.KEY_DELETE, keys.KEY_BACKSPACE):
            if self.inputted:
                self.inputted.pop()
            return False

        if k != keys.KEY_ENTER:
            self.inputted.append(chr(k))
            return False

        return True

    @property
    def place_color(self):
        return curses.color_pair(8)

    @property
    def input(self):
        return ''.join(self.inputted)

    def get(self):
        return self.input


def main(stdscr):
    # import string
    import sys
    import atexit
    inputter = Inputer('test', padding=4)
    screen = Screen(stdscr)

    atexit.register(lambda: sys.stdout.write(str(inputter.input)))
    while True:
        with screen.handle(inputter.handler) as s:
            s.clear()
            inputter.render(s)

if __name__ == '__main__':
    from wordz.screen import Screen
    from wordz.bashlog import filelogger, stdoutlogger, DEBUG
    from wordz.main import redirect
    redirect()
    stdoutlogger(None, DEBUG)
    # filelogger('/tmp/wordz.log', None, DEBUG)
    curses.wrapper(main)

