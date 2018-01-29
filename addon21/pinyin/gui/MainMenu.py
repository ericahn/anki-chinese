from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

from .forms import ruby
from .RubyPreview import RubyPreview

class MainMenu(QDialog):
    def __init__(self, cm):
        QDialog.__init__(self, mw, Qt.Window)
        mw.setupDialogGC(self)
        self.form = ruby.Ui_Dialog()
        self.form.setupUi(self)

        # Environment variables
        # TODO: Clean this up
        self.mw = mw
        self.parent = mw
        self.col = self.mw.col
        self.chinese_master = cm

        # Show main menu
        self.show()
        self.setFocus()

        # Initialize objects
        decks = self.col.decks.all()
        deck_pairs = [(deck['id'], deck['name']) for deck in decks]
        self.deck_ids, self.deck_names = zip(*sorted(deck_pairs, key=lambda a: a[1]))
        self.pinyin_option = None
        self.cedict_enabled = False
        self.primed = False

        self.notes = [[], []]
        self.rubies = [[], []]
        self.tables = [[], []]

        # Set the event listeners
        self.form.deck_combobox.currentIndexChanged.connect(self.deck_selected)
        self.form.note_combobox.currentIndexChanged.connect(self.note_selected)
        self.form.field_combobox.currentIndexChanged.connect(self.field_selected)

        self.form.pinyin_match_combobox.currentIndexChanged.connect(self.pinyin_match_selected)
        self.form.pinyin_generate_combobox.currentIndexChanged.connect(self.pinyin_generate_selected)

        self.form.ruby_combobox.currentIndexChanged.connect(self.ruby_selected)

        self.form.cedict_checkbox.stateChanged.connect(self.cedict_check)

        self.form.list_match.currentRowChanged.connect(self.list_match_selected)
        self.form.list_generate.currentRowChanged.connect(self.list_generate_selected)

        self.form.button_match.clicked.connect(self.execute_match)
        self.form.button_generate.clicked.connect(self.execute_generate)

        self.form.deck_combobox.addItems(self.deck_names)

        # Pinyin selection
        self.form.pinyin_option.buttonClicked.connect(self.pinyin_option_selected)
        self.form.pinyin_match_combobox.hide()
        self.form.pinyin_match_label.hide()
        self.form.widget_match.hide()
        self.form.pinyin_generate_combobox.hide()
        self.form.pinyin_generate_label.hide()
        self.form.widget_generate.hide()

        # CEDICT selection
        self.form.cedict_combobox.hide()
        self.form.cedict_label.hide()

        # Output preview
        self.form.preview_match = RubyPreview()
        self.form.preview_generate = RubyPreview()
        self.form.preview_match_layout.addWidget(self.form.preview_match, 5)
        self.form.preview_generate_layout.addWidget(self.form.preview_generate, 5)

    def deck_selected(self, deck_index):
        did = self.deck_ids[deck_index]
        self.model_ids = []
        self.model_fields = []
        model_names = []
        for cid in self.col.decks.cids(did):
            card = self.col.getCard(cid)
            model = card.model()
            if model['id'] in self.model_ids:
                continue
            self.model_ids.append(model['id'])
            self.model_fields.append([field['name'] for field in model['flds']])
            model_names.append(model['name'])

        self.form.note_combobox.clear()
        self.form.note_combobox.addItems(model_names)

    def note_selected(self, note_index):
        self.form.field_combobox.clear()
        self.form.pinyin_match_combobox.clear()
        self.form.pinyin_generate_combobox.clear()
        self.form.ruby_combobox.clear()
        self.form.cedict_combobox.clear()
        if note_index >= 0:
            self.form.field_combobox.addItems(self.model_fields[note_index])
            self.form.pinyin_match_combobox.addItems(self.model_fields[note_index])
            self.form.pinyin_generate_combobox.addItems(self.model_fields[note_index])
            self.form.ruby_combobox.addItems(self.model_fields[note_index])
            self.form.cedict_combobox.addItems(self.model_fields[note_index])

    def field_selected(self, field_index):
        self.update_actions()

    def pinyin_option_selected(self, radio):
        if radio == self.form.radio_match_strict:
            self.form.pinyin_match_combobox.show()
            self.form.pinyin_match_label.show()
            self.form.widget_match.show()
            self.form.pinyin_generate_combobox.hide()
            self.form.pinyin_generate_label.hide()
            self.form.widget_generate.hide()
            self.pinyin_option = 'strict'
        elif radio == self.form.radio_match_fallback:
            self.form.pinyin_match_combobox.show()
            self.form.pinyin_match_label.show()
            self.form.widget_match.show()
            self.form.pinyin_generate_combobox.show()
            self.form.pinyin_generate_label.show()
            self.form.widget_generate.show()
            self.pinyin_option = 'fallback'
        elif radio == self.form.radio_generate:
            self.form.pinyin_match_combobox.hide()
            self.form.pinyin_match_label.hide()
            self.form.widget_match.hide()
            self.form.pinyin_generate_combobox.show()
            self.form.pinyin_generate_label.show()
            self.form.widget_generate.show()
            self.pinyin_option = 'generate'
        else:
            print('Pinyin option not among radio boxes?')
            return
        self.update_actions()

    def cedict_check(self, state):
        if state == 0:
            self.form.cedict_combobox.hide()
            self.form.cedict_label.hide()
            self.cedict_enabled = False
        elif state == 2:
            self.form.cedict_combobox.show()
            self.form.cedict_label.show()
            self.cedict_enabled = True
            print('Cedict!')
        else:
            print('Unknown CEDICT checkbox state', state)
            return
        self.update_render()

    def ruby_selected(self, ruby_index):
        self.update_actions()

    def pinyin_match_selected(self, pinyin_match_index):
        self.update_actions()

    def pinyin_generate_selected(self, pinyin_generate_index):
        self.update_actions()

    def update_actions(self):
        self.form.list_match.clear()
        self.form.list_generate.clear()

        deck = self.form.deck_combobox.currentText()
        note = self.form.note_combobox.currentText()
        hanzi = self.form.field_combobox.currentText()
        ruby = self.form.ruby_combobox.currentText()

        pinyin_match = self.form.pinyin_match_combobox.currentText()
        pinyin_generate = self.form.pinyin_generate_combobox.currentText()

        if not (deck and note and hanzi and ruby):
            print('Some field not yet selected')
            return

        if self.pinyin_option == 'strict':
            if not pinyin_match:
                print('Existing pinyin field not selected')
                return
            self.stage = self.chinese_master.stage_match_strict(deck, note, hanzi, pinyin_match)
        elif self.pinyin_option == 'fallback':
            if not (pinyin_match and pinyin_generate):
                print('Existing pinyin field or new pinyin field not selected')
                return
            self.stage = self.chinese_master.stage_match_fallback(deck, note, hanzi, pinyin_match)
        elif self.pinyin_option == 'generate':
            if not pinyin_generate:
                print('New pinyin field not selected')
                return
            self.stage = self.chinese_master.stage_generate(deck, note, hanzi)
        else:
            print('Unknown pinyin option set!', self.pinyin_option)
            return

        self.notes = [[], []]
        self.rubies = [[], []]
        self.tables = [[], []]

        for k in range(2):
            flags = {'strict': [True, False], 'fallback': [True, True], 'generate': [False, True]}
            flag = flags[self.pinyin_option][k]
            if not flag:
                continue
            list_widget = [self.form.list_match, self.form.list_generate][k]
            job_type = ['match', 'generate'][k]
            if job_type not in self.stage:
                print('Unknown job type: [{}]. Staged jobs: [{}]'.format(job_type, self.stage.keys()))
                return
            for note, ruby, table in self.stage[job_type]:
                self.notes[k].append(note)
                self.rubies[k].append(ruby)
                self.tables[k].append(table)
            list_widget.addItems([note[hanzi] for note in self.notes[k]])
            label = [self.form.count_label_match, self.form.count_label_generate][k]
            count = len(self.stage[job_type])
            plural = '' if count == 0 else 's'
            descriptor = ['matching', 'empty or non-matching'][k]
            label.setText('Found {} note{} with {} pinyin.'.format(count, plural, descriptor))

        self.primed = True

    def list_match_selected(self, index):
        ruby = self.rubies[0][index]
        table = self.tables[0][index] if self.cedict_enabled else None
        self.form.preview_match.render(ruby, table)

    def list_generate_selected(self, index):
        ruby = self.rubies[1][index]
        table = self.tables[1][index] if self.cedict_enabled else None
        self.form.preview_generate.render(ruby, table)

    def update_render(self):
        for k in range(2):
            flags = {'strict': [True, False], 'fallback': [True, True], 'generate': [False, True]}
            flag = flags[self.pinyin_option][k]
            if not flag:
                continue
            list_widget = [self.form.list_match, self.form.list_generate][k]
            update_method = [self.list_match_selected, self.list_generate_selected][k]
            index = list_widget.currentRow()
            if index >= 0:
                update_method(index)

    def execute_match(self):
        total = len(self.notes[0])
        if self.pinyin_option == 'fallback':
            total += len(self.notes[1])
        if total == 0:
            print('No cards to work on?')
            return
        deck = self.form.deck_combobox.currentText()
        note = self.form.note_combobox.currentText()
        hanzi = self.form.field_combobox.currentText()
        ruby = self.form.ruby_combobox.currentText()
        if self.cedict_enabled:
            cedict = self.form.cedict_combobox.currentText()
        else:
            cedict = None
        key = (deck, note, hanzi)
        self.chinese_master.execute_match(key, ruby, cedict)
        showInfo('Worked on {} notes'.format(total))

    def execute_generate(self):
        total = len(self.notes[1])
        if total == 0:
            print('No cards to work on?')
            return
        deck = self.form.deck_combobox.currentText()
        note = self.form.note_combobox.currentText()
        hanzi = self.form.field_combobox.currentText()
        ruby = self.form.ruby_combobox.currentText()
        if self.cedict_enabled:
            cedict = self.form.cedict_combobox.currentText()
        else:
            cedict = None
        key = (deck, note, hanzi)
        self.chinese_master.execute_generate(key, ruby, None, cedict)
        showInfo('Worked on {} notes'.format(total))
