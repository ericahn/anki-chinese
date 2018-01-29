import os

try:
    # import the main window object (mw) from aqt
    from aqt import mw
    # import the "show info" tool from utils.py
    from aqt.utils import showInfo
    # import all of the Qt GUI library
    from aqt.qt import *
    from .gui import *
except ImportError:
    print('Failed to import Anki modules')
    mw = None

from .chinese_master import ChineseMaster

module_path = os.path.join(os.path.dirname(__file__), '..', 'user_files')

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
    action.triggered.connect(lambda: MainMenu(ChineseMaster(mw, module_path)))
    chinese_menu.addAction(action)