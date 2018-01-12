import re
import unicodedata

from collections import defaultdict


class ChineseDict:

    def __init__(self, lines):
        rex_entry = re.compile(r"^(\S+)\s+(\S+)\s+\[(.+)\]\s+\/(.+)/")
        matches = [rex_entry.match(line) for line in lines if not line.startswith('#')]
        self.entries = defaultdict(lambda: defaultdict(list))
        for match in matches:
            word = match.group(2)
            pinyin = tuple(match.group(3).split(' '))
            definitions = match.group(4).split('/')
            self.entries[word][pinyin].append(definitions)
        for word in self.entries:
            self.entries[word] = dict(self.entries[word])
        self.entries = dict(self.entries)
        self.max_word_length = max(map(len, self.entries))

    def lookup(self, chinese, pinyin=None):
        if pinyin and (chinese, pinyin) in self.entries:
            return True, self.entries[(chinese, pinyin)]
        elif chinese in self.entries:
            return True, self.entries[chinese]
        return False, None

    def gen_words(self, text):
        i = 0
        while i < len(text):
            for j in range(i+self.max_word_length,i,-1):
                s = text[i:j]
                if s in self.entries:
                    yield s
                    break
            i = j