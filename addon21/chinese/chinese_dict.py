import re

from collections import defaultdict


def sort_entry(entry_dict):
    entry = list(entry_dict.items())

    def key(pair):
        pinyins, definitions = pair
        definition_text = ' '.join(map(' '.join, definitions))

        lower = sum(pinyin == pinyin.lower() for pinyin in pinyins)
        size = sum(map(len, definitions))

        grammar_words = 'modal', 'particle', 'clause', 'marker', 'prefix for'
        grammar = sum(grammar_word in definition_text for grammar_word in grammar_words)

        return lower, grammar, size

    return sorted(entry, key=key, reverse=True)


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
        if chinese not in self.entries:
            return False, None
        entry = self.entries[chinese]
        if pinyin and pinyin in entry:
            return True, {pinyin: entry[pinyin]}
        else:
            return True, sort_entry(entry)

    def gen_words(self, text):
        i = 0
        while i < len(text):
            for j in range(i+self.max_word_length,i,-1):
                s = text[i:j]
                if s in self.entries:
                    yield s
                    break
            i = j