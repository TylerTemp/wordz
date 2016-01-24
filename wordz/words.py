import json
import random
from sys import version_info

if version_info[0] < 3:
    from codecs import open

class Words(object):

    def __init__(self, fname):
        with open(fname, 'r', encoding='utf-8') as f:
            self.current = json.load(f)
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
        del self._next_round

    def record(self, word, put_back):
        index = self.words.index(word)
        num = self._record.get(index, 0) + 1
        self._record[index] = num
        if put_back:
            self._next_round.append(word)
