import json
import random
import logging
from sys import version_info
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

if version_info[0] < 3:
    from codecs import open

logger = logging.getLogger('words')

class Words(object):

    BLACK_SQURE = '\u2588'

    def __init__(self, fnames, start=0, end=None):
        saved = []
        for fname in fnames:
            if hasattr(fname, 'read'):
                current = json.load(fname)
            else:
                with open(fname, 'r', encoding='utf-8') as f:
                    current = json.load(f)

            saved.extend(current)

        if end is None:
            self.current = saved[start:]
        else:
            self.current = saved[start:end]

        self.words = list(self.current)
        self._next_round = []
        self._record = {}

    def shuffle(self):
        random.shuffle(self.current)

    def ascend(self):
        return self._sort(False)

    def descend(self):
        return self._sort(True)

    def _sort(self, reverse=False):
        self.current.sort(key=lambda k: k['spell'][0], reverse=reverse)

    def done(self):
        return not self.current and not self._next_round

    def next(self):
        return self.current.pop()

    def next_round(self):
        self.current.extend(self._next_round)
        del self._next_round[:]

    def record(self, word, put_back):
        index = self.words.index(word)
        num = self._record.get(index, 0) + 1
        self._record[index] = num
        if put_back:
            self._next_round.append(word)

    def render_record(self, width):
        f = StringIO()
        write = f.write

        record = self._record
        logger.debug(record)
        if not record:
            wrong_num = 0
        else:
            wrong_num = sum(record.values())

        total = len(self.words)
        right = total - len(record)
        write('Accuracy: %.2f%%(%s/%s)\n' % (right * 100. / total, right, total))
        write(self._get_bar(right * width / total, width))
        write('\n\n')

        words = self.words
        for word_index, num in record.items():
            word = words[word_index]
            write(';'.join(word['spell']))
            if word['pronounce']:
                write(' /%s/' % word['pronounce'])

            write('  (%.2f%% | %s)\n' % (num * 100. / wrong_num, num))

            write(self._get_bar(num * width / wrong_num, width))
            write('\n\n')

        return f.getvalue()

    def _get_bar(self, fill, length):
        fill = int(fill)
        return '%s%s' % (self.BLACK_SQURE * fill, ' ' * (length - fill))

    def formal_record(self):
        return [self.words[index] for index in self._record]


if __name__ == '__main__':
    from io import StringIO
    files = []
    for obj in (
        list(range(3)),
        'abced',
        'ABCDE'
    ):
        f = StringIO(json.dumps(obj))
        f.seek(0)
        files.append(f)

    ins = Words(files, 11)

    print(ins.current)
