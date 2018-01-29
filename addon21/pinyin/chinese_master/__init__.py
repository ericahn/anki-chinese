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
        cedict_path = os.path.join(module_path, 'cedict_ts.u8')
        self.cedict = ChineseDict(codecs.open(cedict_path, 'r', 'utf-8'))
        if jieba_import:
            jieba_path = os.path.join(module_path, 'jieba_extra.u8')
            jieba.load_userdict(jieba_path)