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
        self.something = ruby.Ui_Dialog()
        self.something.setupUi(self)
        print('I exist!')
