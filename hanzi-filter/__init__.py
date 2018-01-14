# import the main window object (mw) from aqt
from aqt import mw

# import the "show info" tool from utils.py
from aqt.utils import showInfo

# import all of the Qt GUI library
from aqt.qt import *


def is_hanzi(c):
    return len(c) == 1 and 0x4e00 <= ord(c) <= 0x9fff


def hanzi_search(col, q):
    cids = col.findCards('deck:Mandarin::Heisig card:Reading {}'.format(q))
    candidates = [col.getCard(cid).note()['Hanzi'] for cid in cids]
    return list(filter(is_hanzi, candidates))


def know_sentence(sentence, known_hanzi):
    return all(not is_hanzi(c) or c in known_hanzi for c in sentence)


def filter_deck(col, known_hanzi, query, field):
    known = []
    unknown = []
    for cid in col.findCards('{}'.format(query)):
        if know_sentence(col.getCard(cid).note()[field], known_hanzi):
            known.append(cid)
        else:
            unknown.append(cid)
    return known, unknown


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def my_filter(col):
    return filter_deck(col,
                       hanzi_search(mw.col, 'is:review'),
                       '"deck:Mandarin::The Incredibles"',
                       'foreign_curr')


def test_function():
    known, unknown = my_filter(mw.col)
    to_show = 'Legible cards: {}/{}'.format(len(known), len(known) + len(unknown))
    showInfo(to_show)


def actual_function():
    known, unknown = my_filter(mw.col)
    mw.col.sched.suspendCards(unknown)
    mw.col.sched.unsuspendCards(known)
    to_show = 'Legible cards: {}/{}'.format(len(known), len(known) + len(unknown))
    showInfo('Did ' + to_show)


for function, menu_name in ((test_function, 'test'),
                            (actual_function, 'actual')):
    # create a new menu item, "test"
    action = QAction(menu_name, mw)

    # set it to call testFunction when it's clicked
    action.triggered.connect(function)

    # and add it to the tools menu
    mw.form.menuTools.addAction(action)
