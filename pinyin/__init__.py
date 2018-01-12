import os
import codecs
import re

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

import dragonmapper.transcriptions
import jieba
jieba.setLogLevel(60)


from pinyin.chinese_dict import ChineseDict
from pinyin.html import *


cedict_path = os.path.join(os.path.dirname(__file__), 'user_files', 'cedict_ts.u8')
cedict = ChineseDict(codecs.open(cedict_path, 'r', 'utf-8'))


def is_hanzi(c):
    return len(c) == 1 and 0x4e00 <= ord(c) <= 0x9fff


def parse_sentence(sentence):
    ruby_struct = []
    for text in jieba.cut(sentence):
        if is_hanzi(text[0]):
            success, pinyins = cedict.lookup(text)
            if success:
                pinyin = list(pinyins.keys())[0]
            else:
                pinyin = [list(cedict.lookup(c)[1])[0] for c in text]
            to_append = (True, text, pinyin)
        else:
            to_append = (False, text, None)
        ruby_struct.append(to_append)
                
    return ruby_struct


def main(col, mw=None):
    if mw:
        config = mw.addonManager.getConfig(__name__)
    
    for config_key in ('deck', 'source_field', 'dest_field', 'dict_field'):
        if config_key not in config:
            return False, 'config.json missing key={}'.format(config_key)

    try:
        cids = col.findCards('"deck:{}"'.format(config['deck']))
    except Exception as e:
        if e.args[0] == 'invalidSearch':
            return False, 'Invalid search'
        else:
            raise

    notes = []
    nids = set()

    for cid in cids:
        note = col.getCard(cid).note()
        if note.id not in nids:
            nids.add(note.id)
            notes.append(note)

    for note in notes:
        missing_fields = []
        for field_key in ('source_field', 'dest_field'):
            field_name = config[field_key]
            if not field_name in note:
                missing_fields.append((field_key, field_name))
        if missing_fields:
            return False, 'Missing fields: {}'.format(', '.join('[{}={}]'.format(a, b) for (a, b) in missing_fields))

    count = 0
    for note in notes:
        ruby_struct = parse_sentence(note[config['source_field']])
        note[config['dest_field']] = generate_ruby(ruby_struct)
        note[config['dict_field']] = generate_definitions_table(cedict, ruby_struct)
        note.flush()
        count += 1
    return True, 'Worked on {} notes'.format(count)


def menu_main():
    if mw is None:
        print('Not running within Anki, exiting.')
        return
    try:
        col = mw.col
    except AttributeError:
        print('Not running within Anki, exiting.')
        return
    status, res = main(col, mw)
    showInfo('Success: {}\n{}'.format(status, res))

if __name__ == '__main__':
    # create a new menu item
    action = QAction("Generate ruby", mw)
    # set it to call testFunction when it's clicked
    action.triggered.connect(menu_main)
    # and add it to the tools menu
    mw.form.menuTools.addAction(action)
