import os
import codecs

try:
    import jieba
    jieba.setLogLevel(60)
except ImportError:
    jieba_import = False
else:
    jieba_import = True

try:
    # import the main window object (mw) from aqt
    from aqt import mw
    # import the "show info" tool from utils.py
    from aqt.utils import showInfo
    # import all of the Qt GUI library
    from aqt.qt import *
except ImportError:
    print('Failed to import Anki modules')

from .chinese_dict import ChineseDict
from .html import generate_ruby, generate_definitions_table
from .gui import *

module_path = os.path.join(os.path.dirname(__file__), '..', 'user_files')

cedict_path = os.path.join(module_path, 'cedict_ts.u8')
cedict = ChineseDict(codecs.open(cedict_path, 'r', 'utf-8'))

if jieba_import:
    jieba_path = os.path.join(module_path, 'jieba_extra.u8')
    jieba.load_userdict(jieba_path)

env = None

if mw:
    chinese_menu = None
    for action in mw.form.menuTools.actions():
        menu = action.menu()
        if menu is not None and action.text() == 'Chinese tools':
            chinese_menu = menu
    if chinese_menu is None:
        chinese_menu = QMenu('Chinese tools')
        mw.form.menuTools.addSeparator()
        mw.form.menuTools.addMenu(chinese_menu)

    action = QAction("Pinyin helper", mw)
    action.triggered.connect(lambda: MainMenu(env))
    chinese_menu.addAction(action)