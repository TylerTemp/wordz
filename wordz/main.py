import curses
import sys
import atexit
import logging
import random
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
from wordz.tracemore import get_exc_plus
from wordz.screen import Screen
from wordz.config import Config
from wordz.inputer import Inputer
from wordz.single_select import SingleSelect
from wordz.words import Words
from wordz import keys

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
    redirect()
    words = Words('words2.json')
    config = Config()
    screen_ui = Screen(stdscr)
    logger.debug('enter config')
    while not config.done():
        with screen_ui.handle(config.handler) as screen:
            screen.clear()
            config.render(screen)

        logger.debug('type: %s; order: %s; repeat: %s',
                     config.quiz_type, config.order_by, config.repeat_wrong)
    else:
        sort(words, config)

    current = True
    prev = None
    while current:
        current = next_word(words, config)
        logger.debug('current: %s', current)
        if current is None:
            continue

        status = {'word': current, 'title': None, 'ui': None,
                  'answer': None, 'input': None, 'content': None}
        parse_status(status, words, config)

        logger.debug(status)
        ui = status['ui']

        while status['input'] is None:
            with screen_ui.handle(lambda k: handle_quiz(k, ui, status)) as _screen:
                _screen.clear()
                _screen.write('[ Quiz ]'.center(screen_ui.width, '='),
                              curses.color_pair(5))
                _screen.write('\n')
                _screen.write(status['title'])
                _screen.write('\n\n')
                ui.render(_screen)

                _screen.write('\n\n')
                render_bar(words, prev, _screen)

                if prev:
                    _screen.write('\n')
                    render_prev(prev, _screen)

        logger.debug(status)
        is_right = status['input'] in status['answer']
        if not is_right:
            if status['content']:
                right = status['content'][status['answer'][0]]
                wrong = status['content'][status['input']]
            else:
                right = '; '.join(status['answer'])
                wrong = status['input']
            prev = {'title': status['title'],
                    'right': right,
                    'wrong': wrong}
            if config.repeat:
                words.record(status['word'], config.repeat)
        else:
            prev = None

    

def handle_quiz(k, ui, status):
    if k == keys.KEY_TAB:
        pass
    elif k == keys.KEY_ESCAPE:
        pass
    elif k == keys.KEY_ENTER:
        status['input'] = ui.get()
    else:
        ui.handler(k)

def sort(words, config):
    if config.order_by == config.SHUFFLE:
        words.shuffle()
    elif config.order_by == config.ASCEND:
        words.ascend()
    elif config.order_by == config.DESCEND:
        words.descend()

def next_word(words, config):
    if words.done():
        return None

    if not words.current:
        words.next_round()
        sort(words, config)
        return words.next()

    return words.next()

def parse_status(status, words, config):
    this_word = status['word']
    all_words = words.words

    quiz_type = []
    for q_type, allow in config.get_quiz_type().items():
        if allow:
            quiz_type.append(q_type)

    this_quiz_type = random.choice(quiz_type)
    logger.debug(this_quiz_type)
    if this_quiz_type == 'spell':
        status['title'] = parse_meaning(this_word)
        status['ui'] = Inputer('You answer', 4)
        status['answer'] = this_word['spell']
    elif this_quiz_type.startswith('choose'):
        if len(all_words) <= 4:
            options = all_words
        else:
            options = [this_word]
            while len(options) != 4:
                guess = random.choice(all_words)
                if guess not in options:
                    options.append(guess)

        status['answer'] = [options.index(this_word)]
        if this_quiz_type == 'choose_word':
            status['title'] = parse_meaning(this_word)
            to_choose = [parse_spell(x) for x in options]
        else:
            status['title'] = parse_spell(this_word)
            to_choose = [parse_meaning(x) for x in options]
        status['content'] = to_choose
        status['ui'] = SingleSelect(to_choose, padding=2)

def parse_meaning(word):
    result = []
    for k, v in word['meaning'].items():
        if k is None:
            result.append(v)
        else:
            result.append('[%s] %s' % (k, '; '.join(v)))

    return '\n'.join(result)

def parse_spell(word):
    result = ''.join(word['spell'])
    if word['pronounce']:
        result = ''.join((result, ' /', word['pronounce'], '/'))
    return result

def render_bar(words, error, screen):
    total = len(words.words)
    rest = len(words.current) + len(words._next_round) + 1
    checked = total - rest
    width = screen.width - 2
    num_str = '%s/%s' % (checked, total)
    filled_str = '>' * (checked * width // total)
    white_len = width - len(filled_str)
    white_str = num_str.rjust(white_len)
    if len(white_str) > white_len:
        white_str = ' ' * white_len

    write_str = '[%s%s]' % (filled_str, white_str)
    if error:
        screen.write(write_str, curses.color_pair(2))
    else:
        screen.write(write_str)

def render_prev(prev, screen):
    screen.write(prev['title'])
    screen.write('\n\u2717 ' + prev['wrong'], curses.color_pair(2))
    screen.write('\n\u2713 ' + prev['right'], curses.color_pair(3))


def get_key(stdscr):

    def print_key(k):
        print(repr(k))
        print(repr(chr(k)))
        # print(ord(chr(k)))
        for each in dir(curses):
            # if each.startswith('KEY_'):
            if getattr(curses, each) == k:
                print(each)
                return

    redirect()

    with Screen(stdscr).handle(print_key) as s:
        # s.write('line' * 70, True)
        s.write('Enter a key:', curses.color_pair(3))
        # print('\n'.join(dir(s.stdscr)))
        # s.refresh()


if __name__ == '__main__':
    from wordz.bashlog import stdoutlogger, filelogger, DEBUG
    open('/tmp/wordz.log', 'w').close()
    stdoutlogger(None, DEBUG)
    filelogger('/tmp/wordz.log')
    curses.wrapper(main)
    # curses.wrapper(get_key)
    # main()