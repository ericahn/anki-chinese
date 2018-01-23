try:
    # import the main window object (mw) from aqt
    from aqt import mw
    # import the "show info" tool from utils.py
    from aqt.utils import showInfo
    # import all of the Qt GUI library
    from aqt.qt import *
except ImportError:
    print('Failed to import Anki modules')

from . import ruby


class MainMenu(QDialog):
    def __init__(self):
        QDialog.__init__(self, mw, Qt.Window)
        mw.setupDialogGC(self)
        self.form = ruby.Ui_Dialog()
        self.form.setupUi(self)

        self.mw = mw
        self.parent = mw
        self.col = self.mw.col

        self.show()
        self.setFocus()

        self.form.deck_combobox.setStyleSheet("combobox-popup: 0;")

        decks = self.col.decks.all()
        self.deck_ids, self.deck_names = zip(*sorted([(deck['id'], deck['name']) for deck in decks],
                                                     key=lambda a: a[1]))

        # Set the event listeners
        self.form.deck_combobox.currentIndexChanged.connect(self.deck_selected)
        self.form.note_combobox.currentIndexChanged.connect(self.note_selected)
        self.form.field_combobox.currentIndexChanged.connect(self.field_selected)
        self.form.deck_combobox.addItems(self.deck_names)

        self.form.pinyin_option.buttonClicked.connect(self.pinyin_option_selected)

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
        if note_index >= 0:
            self.form.field_combobox.addItems(self.model_fields[note_index])

    def field_selected(self, field_index):
        field = self.form.field_combobox.currentText()
        deck_name = self.form.deck_combobox.currentText()
        note_name = self.form.note_combobox.currentText()

        if '' in (field, note_name):
            return

        cids = self.col.findCards('deck:"{}" note:"{}" is:review'.format(deck_name, note_name))
        candidates = [self.col.getCard(cid).note()[field] for cid in cids]
        # self.update_actions()

    def pinyin_option_selected(self, *args):
        print(args)