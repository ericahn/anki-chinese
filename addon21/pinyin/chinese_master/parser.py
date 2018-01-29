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


def parse_sentence(cedict, sentence):
    ruby_struct = []
    for text in jieba.cut(sentence):
        if is_hanzi(text[0]):
            success, pinyins = cedict.lookup(text)
            if success:
                pinyin = pinyins[0][0]
                ruby_struct.append((True, text, pinyin))
            else:
                for word in cedict.gen_words(text):
                    ruby_struct.append((True, word, cedict.lookup(word)[1][0][0]))
        elif text[0] == '?' and len(ruby_struct) > 0 and ruby_struct[-1][1] == '吗':
            ruby_struct[-1] = (True, '吗', ('ma5',))
        else:
            ruby_struct.append((False, text, None))

    return ruby_struct


def match_hp(hanzi_raw, pinyin_raw, debug=False):
    hanzis = re.findall('[{}]'.format(zhon.hanzi.characters), hanzi_raw)
    pinyins = re.findall(zhon.pinyin.syllable, pinyin_raw, re.I)
    if debug: print(hanzis)
    if debug: print(pinyins)
    if len(hanzis) != len(pinyins):
        return False, None
    output = []
    in_match = True
    while hanzis and pinyins:
        hanzi = hanzis[0]
        pinyin = pinyins[0]
        hanzi_match = hanzis[0] == hanzi_raw[0]
        pinyin_match = pinyins[0] == pinyin_raw[:len(pinyin)]
        if debug: print('So far: {}'.format(output))
        if debug: print('  Hanzi : [{}] [{}] {}'.format(hanzi, hanzi_raw[0], hanzi_match))
        if debug: print('  Pinyin: [{}] [{}] {}'.format(pinyin, pinyin_raw[:len(pinyin)], pinyin_match))
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
            output[-1][1].append(hanzi)
            hanzi_raw = hanzi_raw[1:]
        elif not pinyin_match:
            if len(output) == 0 or output[-1][0]:
                output.append([False, [], []])
            output[-1][2].append(pinyin_raw[0])
            pinyin_raw = pinyin_raw[1:]
        if debug: print('')
    if hanzis or pinyins:
        return False, output
    if output[-1][0]:
        output.append([False, [], []])
    output[-1][1].append(hanzi_raw.split())
    output[-1][2].append(pinyin_raw.split())
    return True, output
