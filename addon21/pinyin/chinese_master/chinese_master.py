import os
import codecs

try:
    import pinyinhelper.jieba as jieba
except ImportError:
    try:
        import jieba
    except ImportError:
        jieba_import = False
        print('Could not find jieba!')
    else:
        jieba_import = True
else:
    jieba_import = True
if jieba_import:
    jieba.setLogLevel(60)


from .chinese_dict import ChineseDict
from .parser import *
from .html import *


class ChineseMaster:
    def __init__(self, col, module_path):
        self.col = col
        cedict_path = os.path.join(module_path, 'cedict_ts.u8')
        self.cedict = ChineseDict(codecs.open(cedict_path, 'r', 'utf-8'))
        if jieba_import:
            jieba_path = os.path.join(module_path, 'jieba_extra.u8')
            jieba.load_userdict(jieba_path)
        self.staged = {}

    def stage_match_strict(self, deck, note, hanzi_field, pinyin_field):
        nids = set()
        stage_key = (deck, note, hanzi_field)
        match_stage = []
        match_key = "match"
        for cid in self.col.findCards('deck:"{}" note:"{}"'.format(deck, note)):
            note = self.col.getCard(cid).note()
            if note.id in nids or len(note[pinyin_field]) <= 1:
                continue
            nids.add(note.id)
            success, match = match_hp(note[hanzi_field], note[pinyin_field])
            if success:
                ruby_struct = clean_match(match)
                ruby = generate_ruby(ruby_struct)
                table = generate_definitions_table(self.cedict, ruby_struct)
                match_stage.append([note, ruby, table])
        stage = {match_key: match_stage}
        self.staged[stage_key] = stage
        return stage

    def stage_match_fallback(self, deck, note, hanzi_field, pinyin_field):
        nids = set()

        stage_key = (deck, note, hanzi_field)

        match_stage = []
        match_key = "match"

        gen_stage = []
        gen_key = "generate"

        for cid in self.col.findCards('deck:"{}" note:"{}"'.format(deck, note)):
            note = self.col.getCard(cid).note()
            if note.id in nids:
                continue
            success, match = match_hp(note[hanzi_field], note[pinyin_field])
            if success:
                ruby_struct = clean_match(match)
                stage = match_stage
            else:
                ruby_struct = parse_sentence(self.cedict, note[hanzi_field])
                stage = gen_stage
            ruby = generate_ruby(ruby_struct)
            table = generate_definitions_table(self.cedict, ruby_struct)
            stage.append([note, ruby, table])

        stage = {match_key: match_stage, gen_key: gen_stage}
        self.staged[stage_key] = stage
        return stage

    def stage_generate(self, deck, note, hanzi_field):
        nids = set()

        stage_key = (deck, note, hanzi_field)

        gen_stage = []
        gen_key = "generate"

        for cid in self.col.findCards('deck:"{}" note:"{}"'.format(deck, note)):
            note = self.col.getCard(cid).note()
            if note.id in nids:
                continue

            ruby_struct = parse_sentence(self.cedict, note[hanzi_field])
            ruby = generate_ruby(ruby_struct)
            table = generate_definitions_table(self.cedict, ruby_struct)
            gen_stage.append([note, ruby, table])

        stage = {gen_key: gen_stage}
        self.staged[stage_key] = stage
        return stage

    def execute_generate(self, key, ruby_field, pinyin_gen_field, cedict_field=None):
        if key not in self.staged:
            return
        for note, ruby, table in self.staged[key]['generate']:
            note[ruby_field] = ruby
            if cedict_field is not None:
                note[cedict_field] = table
            note.flush()

    def execute_match(self, key, ruby_field, cedict_field=None):
        if key not in self.staged:
            return
        if 'match' in self.staged[key]:
            for note, ruby, table in self.staged[key]['match']:
                note[ruby_field] = ruby
                if cedict_field is not None:
                    note[cedict_field] = table
                note.flush()
        if 'generate' in self.staged[key]:
            for note, ruby, table in self.staged[key]['generate']:
                note[ruby_field] = ruby
                if cedict_field is not None:
                    note[cedict_field] = table
                note.flush()