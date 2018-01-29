import os
import codecs

try:
    import jieba
    jieba.setLogLevel(60)
except ImportError:
    jieba_import = False
    print('Could not find jieba!')
else:
    jieba_import = True
    jieba.setLogLevel(60)


from .chinese_dict import ChineseDict



class ChineseMaster:
    def __init__(self, module_path):
        user_files_path = os.path.join(module_path, 'user_files')
        jieba_path = os.path.join(user_files_path, 'jieba_extra.u8')
        cedict_path = os.path.join(user_files_path, 'cedict_ts.u8')

        jieba.load_userdict(jieba_path)
        self.cedict = ChineseDict(codecs.open(cedict_path, 'r', 'utf-8'))

    def stage_match(self, deck, note, sentence_field, pinyin_field, ruby_field):