import re

try:
    import jieba
    jieba.setLogLevel(60)
except ImportError:
    jieba_import = False
    print('Could not find jieba!')
else:
    jieba_import = True
    jieba.setLogLevel(60)

import zhon


def is_hanzi(c):
    return len(c) == 1 and 0x4e00 <= ord(c) <= 0x9fff


def numbers_to_accent(syllables, joiner=''):
    return joiner.join(map(decode_pinyin, syllables))


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


def parse_sentence(cedict, sentence):
    ruby_struct = []
    for text in jieba.cut(sentence):
        if is_hanzi(text[0]):
            success, pinyins = cedict.lookup(text)
            if success:
                pinyin = numbers_to_accent(pinyins[0][0], ' ')
                ruby_struct.append((True, text, pinyin))
            else:
                for word in cedict.gen_words(text):
                    pinyin = numbers_to_accent(cedict.lookup(word)[1][0][0], ' ')
                    ruby_struct.append((True, word, pinyin))
        elif text[0] == '?' and len(ruby_struct) > 0 and ruby_struct[-1][1] == '吗':
            ruby_struct[-1] = (True, '吗', ('ma5',))
        else:
            ruby_struct.append((False, text, None))

    return ruby_struct


def match_hp(hanzi_raw, pinyin_raw, debug=False):
    hanzis = re.findall('[{}]'.format(zhon.hanzi.characters), hanzi_raw)
    pinyins = re.findall(zhon.pinyin.syllable, pinyin_raw, re.I)
    if debug:
        print(hanzis)
        print(pinyins)
    if len(hanzis) != len(pinyins):
        return False, None
    output = []
    while hanzis and pinyins:
        hanzi = hanzis[0]
        pinyin = pinyins[0]
        hanzi_match = hanzis[0] == hanzi_raw[0]
        pinyin_match = pinyins[0] == pinyin_raw[:len(pinyin)]
        if debug:
            print('So far: {}'.format(output))
            print('  Hanzi : [{}] [{}] {}'.format(hanzi, hanzi_raw[0], hanzi_match))
            print('  Pinyin: [{}] [{}] {}'.format(pinyin, pinyin_raw[:len(pinyin)], pinyin_match))
        if hanzi_match and pinyin_match:
            if len(output) == 0 or not output[-1][0]:
                output.append([True, [], []])
            output[-1][1].append(hanzi)
            output[-1][2].append(pinyin)
            hanzis = hanzis[1:]
            hanzi_raw = hanzi_raw[1:]
            pinyins = pinyins[1:]
            pinyin_raw = pinyin_raw[len(pinyin):]
        elif not hanzi_match:
            if len(output) == 0 or output[-1][0]:
                output.append([False, [], []])
            output[-1][1].append(hanzi_raw[0])
            hanzi_raw = hanzi_raw[1:]
        elif not pinyin_match:
            if len(output) == 0 or output[-1][0]:
                output.append([False, [], []])
            output[-1][2].append(pinyin_raw[0])
            pinyin_raw = pinyin_raw[1:]
    if hanzis or pinyins:
        return False, output
    if output[-1][0]:
        output.append([False, [], []])
    output[-1][1] += hanzi_raw.split()
    output[-1][2] += pinyin_raw.split()
    return True, output


def clean_match(match):
    result = []
    for flag, a, b in match:
        if flag:
            result.append((True, ''.join(a), ' '.join(b)))
        else:
            if not a:
                text = ''.join(b)
            elif not b:
                text = ''.join(a)
            else:
                text = combine_punct(a, b)
            result.append((False, text, None))
    return result


PUNCTS = [('。', '.'),
          ('？', '?'),
          ('，', ', '),
          ('！', '!'),
          ('《', ' "'),
          ('》', '" '),
          ('、', ', '),
          ('；', '; '),
          ('⋯⋯', '... '),
          ('→', ' ￫ '),
          ('，', '. '),
          ('。', '!')]


def combine_punct(a, b, debug=False):
    text = ''
    a = ''.join(a)
    b = ''.join(b)
    while a and b:
        found = False
        if a[0] == b[0]:
            text += a[0]
            a = a[1:]
            b = b[1:]
            continue
        for punct_a, punct_b in PUNCTS:
            if a.startswith(punct_a) and b.startswith(punct_b):
                text += punct_a
                found = True
                break
        if found:
            a = a[len(punct_a):]
            b = b[len(punct_b):]
        else:
            if a in b:
                text += b
                return text
            elif b in a:
                text += a
                return text
            else:
                if debug:
                    print('How to combine? a=[{}], b=[{}]'.format(a, b))
                if len(b) > len(a):
                    b = b[1:]
                else:
                    text += a[0]
                    a = a[1:]
    return text
