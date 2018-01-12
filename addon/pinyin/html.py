def generate_ruby(ruby_struct):
    html = ''
    prev = False
    for is_ruby, main, pinyins in ruby_struct:
        if is_ruby:
            to_add  = ' ' if prev else ''
            to_add += '<ruby>{}<rt>{}</ruby>'.format(main, ''.join(pinyins))
        else:
            to_add = main
        prev = is_ruby
        html += to_add
    return html

def generate_definitions_table(cedict, ruby_struct):
    html = '<table>\n{}</table>'
    inner = ''
    inner_temp = '<tr{}><td class="dict-word">{}</td><td class="dict-definition">{}</td></tr>'.format
    rows = []
    first_word = True
    for chinese, text, pinyins in ruby_struct:
        if not chinese:
            continue
        print(pinyins)
        success, definitions = cedict.lookup(text, pinyins)
        first = True
        if success:
            for definition in definitions:
                for element in definition:
                    word = text if first else ''
                    if first and not first_word:
                        top_border = ' class="dict-word-border"'
                    else:
                        top_border = ''
                    inner += inner_temp(top_border, word, element)
                    first = False
        else:
            words = cedict.gen_words(text)
            

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