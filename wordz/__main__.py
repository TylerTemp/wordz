from wordz.main import main as wordz_main, redirect, __doc__
from wordz.config import Config
from wordz.words import Words
from wordz.bashlog import stdoutlogger, filelogger, DEBUG
import curses
import docpie
import logging

logger = logging.getLogger()
logging.getLogger('docpie').setLevel(logging.CRITICAL)


def get_command():
    pie = docpie.docpie(__doc__)

    if pie['--debug']:
        filelogger(pie['--debug'], logger)

    stdoutlogger(logger, DEBUG)

    logger.debug(pie)
    type_ = []
    if pie['--choose-word']:
        type_.append(Config.CHOOSE_WORD)
    if pie['--choose-meaning']:
        type_.append(Config.CHOOSE_MEANING)
    if not type_:
        type_.append(Config.SPELL)

    assert type_, type_

    if pie['--ascend']:
        order = Config.ASCEND
    elif pie['--descend']:
        order = Config.DESCEND
    else:
        order = Config.SHUFFLE

    config = Config.manual_init(type_=type_, order=order,
                                repeat=not pie['--no-repeat'])

    config.save_file = pie['--out']

    files = pie['<file>']
    start = int(pie['--skip'])
    count = pie['--limit']
    if count.lower() == 'inf':
        end = None
    else:
        count = int(count)
        end = start + count

    words = Words(files, start, end)

    return config, words


def main():
    redirect()
    config, words = get_command()
    # return curses.wrapper(wordz_main, config, words)
    return wordz_main(curses.initscr(), config, words)

if __name__ == '__main__':
    import sys
    sys.exit(main())
