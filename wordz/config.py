import curses
from wordz import keys
from wordz.multi_select import MultiSelect
from wordz.single_select import SingleSelect

class Config(object):
    SPELL = 0
    CHOOSE_WORD = 1
    CHOOSE_MEANING = 2

    SHUFFLE = 0
    ASCEND = 1
    DESCEND = 2

    def __init__(self):
        self.type = MultiSelect(
            ['Give meaning and spell the word',
             'Give meaning and choose the word',
             'Give word and choose the meaning'],
            default=(self.SPELL,), padding=4)
        self.order = SingleSelect(
            ['Shuffle',
             'Ascend',
             'Descend',
            ], default=self.SHUFFLE, padding=4)
        self.repeat = MultiSelect(
            ['Appear a word repeatedly till I answer it right'],
            default=(0,),
            padding=4)

        self.active = self.type
        self.entered = False

    @classmethod
    def manual_init(cls, type_, order, repeat):
        self = cls()
        self.type.select = type_
        self.order.select = order
        self.repeat.select = (0,) if repeat else ()
        self.entered = True
        return self

    def render(self, screen):
        self.render_title(screen)
        screen.write('\n\n')
        self.render_quiz_type(screen)
        screen.write('\n')
        self.render_order(screen)
        screen.write('\n')
        self.render_repeat(screen)

    def render_title(self, screen):
        width = screen.width
        screen.write('[ Config ]'.center(width, '='), self.title_color)

    def render_quiz_type(self, screen):
        screen.write('  Quiz Type:\n', self.active_color if self.active is self.type else None)
        self.type.render(screen)

    def render_order(self, screen):
        screen.write('  Order:\n', self.active_color if self.active is self.order else None)
        self.order.render(screen)

    def render_repeat(self, screen):
        screen.write('  Repeat:\n', self.active_color if self.active is self.repeat else None)
        self.repeat.render(screen)

    @property
    def title_color(self):
        return curses.color_pair(5)

    @property
    def active_color(self):
        return curses.color_pair(13)

    @property
    def quiz_type(self):
        return self.type.select

    @property
    def order_by(self):
        return self.order.select

    @property
    def repeat_wrong(self):
        return bool(self.repeat.select)

    def handler(self, k):
        if k == keys.KEY_TAB:
            order = (self.type, self.order, self.repeat)
            index = order.index(self.active) + 1
            if index > 2:
                index = 0
            self.active = order[index]
        elif k == keys.KEY_ENTER:
            self.entered = True
        else:
            self.active.handler(k)

    def done(self):
        if not self.entered:
            return False
        if not self.quiz_type:
            self.entered = False
            self.active = self.type
            return False
        return True

    def get_quiz_type(self):
        quiz_type = self.quiz_type
        return {
            'spell': self.SPELL in quiz_type,
            'choose_word': self.CHOOSE_WORD in quiz_type,
            'choose_meaning': self.CHOOSE_MEANING in quiz_type,
        }


def main(stdscr):
    config = Config()
    while True:
        with Screen(stdscr).handle(config.handler) as screen:
            screen.clear()
            config.render(screen)

if __name__ == '__main__':
    from wordz.screen import Screen
    from wordz.bashlog import filelogger, stdoutlogger, DEBUG
    from wordz.main import redirect
    
    redirect()
    stdoutlogger(None, DEBUG)
    # filelogger('/tmp/wordz.log', None, DEBUG)
    curses.wrapper(main)
