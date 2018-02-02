import re

try:
    import jieba
except ImportError:
    try:
        from ... import jieba
    except ImportError:
        jieba_import = False
        print('Could not find local jieba')
    except ValueError as err:
        err_msg = err.args[0]
        if 'relative' in err_msg and 'import' in err_msg:
            print('Could not find local jieba with relative import')
            jieba_import = False
        else:
            raise
    else:
        jieba_import = True
else:
    jieba_import = True
if jieba_import:
    jieba.setLogLevel(60)

try:
    import zhon.hanzi as zhonhanzi
    import zhon.pinyin as zhonpinyin
except ImportError:
    from ...zhon import hanzi as zhonhanzi
    from ...zhon import pinyin as zhonpinyin


from .atoms import numbers_to_accent, pinyin_mton, is_hanzi


def parse_sentence(cedict, sentence):
    ruby_struct = []
    for text in jieba.cut(sentence):
        if is_hanzi(text[0]):
            success, pinyins = cedict.lookup(text)
            if success:
                ruby_struct.append((True, text, pinyins[0][0]))
            else:
                for word in cedict.gen_words(text):
                    pinyin = cedict.lookup(word)[1][0][0]
                    ruby_struct.append((True, word, pinyin))
        elif text[0] == '?' and len(ruby_struct) > 0 and ruby_struct[-1][1] == '吗':
            ruby_struct[-1] = (True, '吗', ('ma5',))
        else:
            ruby_struct.append((False, text, None))

    return ruby_struct


def match_hp(hanzi_raw, pinyin_raw, debug=False):
    hanzis = re.findall('[{}]'.format(zhonhanzi.characters), hanzi_raw)
    pinyins = re.findall(zhonpinyin.syllable, pinyin_raw, re.I)
    if len(hanzis) == 0 or len(pinyins) == 0:
        return False, None
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
            output[-1][2].append(pinyin_mton(pinyin).lower())
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
            result.append((True, ''.join(a), tuple(b)))
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
