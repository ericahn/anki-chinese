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

    def stage_match_strict(self, deck, note, hanzi_field, pinyin_field, ruby_field):
        nids = set()
        stage_key = (deck, note, hanzi_field)
        match_stage = []
        match_key = ("match", (ruby_field,))
        stage_key = ((deck, note, hanzi_field), "match", (ruby_field,))
        for cid in self.col.findCards('deck:"{}" note:"{}"'.format(deck, note)):
            note = self.col.getCard(cid).note()
            if note.id in nids or len(note[pinyin_field]) <= 1:
                continue
            nids.add(note.id)
            success, match = match_hp(note[hanzi_field], note[pinyin_field])
            if success:
                match_stage.append([note, clean_match(match)])
        stage = {match_key: match_stage}
        self.staged[stage_key] = stage
        return stage

    def stage_match_fallback(self, deck, note, hanzi_field, pinyin_field, pinyin_gen_field, ruby_field):
        nids = set()

        stage_key = (deck, note, hanzi_field)

        match_stage = []
        match_key = ("match", (ruby_field,))

        gen_stage = []
        gen_key = ("generate", (ruby_field, pinyin_gen_field))

        for cid in self.col.findCards('deck:"{}" note:"{}"'.format(deck, note)):
            note = self.col.getCard(cid).note()
            if note.id in nids:
                continue
            success, match = match_hp(note[hanzi_field], note[pinyin_field])
            if success:
                match_stage.append([note, clean_match(match)])
            else:
                ruby = parse_sentence(self.cedict, note[hanzi_field])
                gen_stage.append([note, ruby])

        stage = {match_key: match_stage, gen_key: gen_stage}
        self.staged[stage_key] = stage
        return stage

    def stage_generate(self, deck, note, hanzi_field, pinyin_gen_field, ruby_field):
        nids = set()

        stage_key = (deck, note, hanzi_field)

        gen_stage = []
        gen_key = ("generate", (ruby_field, pinyin_gen_field))

        for cid in self.col.findCards('deck:"{}" note:"{}"'.format(deck, note)):
            note = self.col.getCard(cid).note()
            if note.id in nids:
                continue

            ruby = parse_sentence(self.cedict, note[hanzi_field])
            gen_stage.append([note, ruby])

        stage = {gen_key: gen_stage}
        self.staged[stage_key] = stage
        return stage

    def execute_staged(self, deck, note, hanzi_field):
        stage_key = (deck, note, hanzi_field)
        if stage_key not in self.staged:
            print('The stage key {} is not in staging area!')
            return
        for (job, fields), todo in self.staged[stage_key].items():
            if job == 'generate':
                ruby_field, pinyin_gen_field = fields
                self.execute_generate(todo, ruby_field, pinyin_gen_field)
            elif job == 'match':
                self.execute_match(todo, fields[0])
            else:
                print('Unknown job type [{}] was staged! It has fields {}'.format(job, fields))
                continue

    def execute_generate(self, todo, ruby_field, pinyin_gen_field):
        for note, ruby_struct in todo:
            note[ruby_field] = generate_ruby(ruby_struct)
            note.flush()

    def execute_match(self, todo, stage_key, ruby_field):
        for note, ruby_struct in todo:
            note[ruby_field] = generate_ruby(ruby_struct)
            note.flush()
