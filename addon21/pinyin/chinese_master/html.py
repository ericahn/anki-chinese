from .atoms import pinyin_ntom


def numbers_to_accent(syllables, joiner=''):
    return joiner.join(map(pinyin_ntom, syllables))


def generate_ruby(ruby_struct):
    html = ''
    prev = False
    for is_ruby, main, pinyins in ruby_struct:
        if is_ruby:
            to_add  = ' ' if prev else ''
            accented = numbers_to_accent(pinyins, ' ')
            to_add += '<ruby>{}<rt>{}</ruby>'.format(main, accented)
        else:
            if main == ' ' or main == '  ':
                to_add = '&nbsp;&nbsp;'
            else:
                to_add = main
        prev = is_ruby
        html += to_add
    return html


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
            for found_pinyins, entries in entry_dict:
                if list(c.lower() for c in found_pinyins) != list(c.lower() for c in pinyins):
                    continue
                for elements in entries:
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
                for pinyin, definitions in entry_dict:
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