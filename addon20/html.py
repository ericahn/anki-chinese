import re


def numbers_to_accent(syllables, joiner=''):
    return joiner.join(map(decode_pinyin, syllables))


def generate_ruby(ruby_struct):
    html = ''
    prev = False
    for is_ruby, main, pinyins in ruby_struct:
        if is_ruby:
            to_add  = ' ' if prev else ''
            to_add += '<ruby>{}<rt>{}</ruby>'.format(main, numbers_to_accent(pinyins, ' '))
        else:
            if main == ' ':
                to_add = '<br />'
            else:
                to_add = main
        prev = is_ruby
        html += to_add
    return html


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


def generate_definitions_table(cedict, ruby_struct):
    html = '<table>\n{}</table>'
    inner = ''

    col_classes = 'dict-table-word', 'dict-table-pinyin', 'dict-table-definition'
    row_temp  = '  <tr class="{}">\n'
    row_temp += '\n'.join('    <td class={}>{{}}</td>'.format(row_class) for row_class in col_classes) + '\n'
    row_temp += '  </tr>\n'

    first = True
    already = set()
    for chinese, text, pinyins in ruby_struct:
        first_word = True
        if not chinese:
            continue
        success, entry_dict = cedict.lookup(text, pinyins)
        if success and text not in already:
            already.add(text)
            for elements in entry_dict[pinyins]:
                if 'variant of' in elements[0]:
                    continue
                ol = '\n      <ol>\n'
                ol += ''.join('        <li>{}</li>\n'.format(element) for element in elements)
                ol += '      </ol>'
                word = text if first_word else ''
                pinyin = numbers_to_accent(pinyins)
                row_class = ''
                if not first and first_word:
                    row_class += 'dict-table-word-border'
                inner += row_temp.format(row_class, word, pinyin, ol)
                first_word = False
                first = False
        else:
            words = cedict.gen_words(text)
            for word in words:
                if word in already:
                    continue
                already.add(word)
                first_word = True
                success, entry_dict = cedict.lookup(word)
                for pinyin, definitions in sort_entry(entry_dict):
                    first_pinyin = True
                    for elements in definitions:
                        if 'variant of' in elements[0]:
                            continue
                        ol = '\n      <ol>\n'
                        ol += ''.join('        <li>{}</li>\n'.format(element) for element in elements)
                        ol += '      </ol>'
                        word = word if first_word else ''
                        pinyin = numbers_to_accent(pinyin)
                        row_class = []
                        if not first:
                            if first_word:
                                row_class.append('dict-table-word-border')
                            elif first_pinyin:
                                row_class.append('dict-table-pinyin-border')
                        inner += row_temp.format(' '.join(row_class), word, pinyin, ol)
                        first_word = False
                        first_pinyin = False
                        first = False

    return html.format(inner)


PinyinToneMark = {
    0: "aoeiuv\u00fc",
    1: "\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6",
    2: "\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8",
    3: "\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da",
    4: "\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc",
}

def decode_pinyin(s):
    s = s.lower()
    r = ""
    t = ""
    for c in s:
        if 'a' <= c <= 'z':
            t += c
        elif c == ':':
            assert t[-1] == 'u'
            t = t[:-1] + "\u00fc"
        else:
            if '0' <= c <= '5':
                tone = int(c) % 5
                if tone != 0:
                    m = re.search("[aoeiuv\u00fc]+", t)
                    if m is None:
                        t += c
                    elif len(m.group(0)) == 1:
                        t = t[:m.start(0)] + PinyinToneMark[tone][PinyinToneMark[0].index(m.group(0))] + t[m.end(0):]
                    else:
                        if 'a' in t:
                            t = t.replace("a", PinyinToneMark[tone][0])
                        elif 'o' in t:
                            t = t.replace("o", PinyinToneMark[tone][1])
                        elif 'e' in t:
                            t = t.replace("e", PinyinToneMark[tone][2])
                        elif t.endswith("ui"):
                            t = t.replace("i", PinyinToneMark[tone][3])
                        elif t.endswith("iu"):
                            t = t.replace("u", PinyinToneMark[tone][4])
                        else:
                            t += "!"
            r += t
            t = ""
    r += t
    return r