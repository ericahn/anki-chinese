def parse_sentence(sentence):
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