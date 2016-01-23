import curses
import sys
import atexit
import logging
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
from wordz.bashlog import stdoutlogger, DEBUG
from wordz.tracemore import get_exc_plus
from wordz.screen import Screen

_real_out = sys.stdout
_real_err = sys.stderr
_fake_out = StringIO()
_fake_err = StringIO()
logger = logging.getLogger()

_REDIRECTED = False


def redirect():
    logger.debug('redirecting...')
    sys.stdout = _fake_out
    sys.stderr = _fake_err
    global _REDIRECTED
    _REDIRECTED = True


@atexit.register
def redirect_restore():
    logger.debug('exiting...')
    if _REDIRECTED:
        _fake_out.seek(0)
        _fake_err.seek(0)
        out = _fake_out.read()
        err = _fake_err.read()
        sys.stdout = _real_out
        sys.stderr = _real_err
        sys.stdout.write(out)
        sys.stderr.write(err)
        tp, value, tb = sys.exc_info()
        if tp is not None:
            sys.stderr(get_exc_plus())
        sys.stdout.flush()
        sys.stderr.flush()
    

def main(stdscr):

    def print_key(k):
        # print(repr(k))
        # print(chr(k))
        # print(ord(chr(k)))
        for each in dir(curses):
            # if each.startswith('KEY_'):
            if getattr(curses, each) == k:
                print(each)
                return
        else:
            print(k)

    redirect()

    with Screen(stdscr).handle(print_key) as s:
        # s.write('line' * 70, True)
        s.write('中')
        print(s.stdscr.getyx())
        s.write('中')
        print(s.stdscr.getyx())
        s.write('中')
        print(s.stdscr.getyx())
        # print('\n'.join(dir(s.stdscr)))
        # s.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
    # main()