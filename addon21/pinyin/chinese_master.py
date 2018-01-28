import os
import codecs

import jieba

from .chinese_dict import ChineseDict

jieba.setLogLevel(60)


class ChineseMaster:
    def __init__(self, module_path):
        user_files_path = os.path.join(module_path, 'user_files')
        jieba_path = os.path.join(user_files_path, 'jieba_extra.u8')
        cedict_path = os.path.join(user_files_path, 'cedict_ts.u8')

        jieba.load_userdict(jieba_path)
        self.cedict = ChineseDict(codecs.open(cedict_path, 'r', 'utf-8'))
