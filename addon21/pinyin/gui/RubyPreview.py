from aqt.qt import *

CSS = '''
table {
    margin-left:auto; 
    margin-right:auto;
    border-collapse: collapse;
  }

tr.dict-table-word-border td {
  border-top:1pt solid black;
}

.dict-table-word {
  white-space:nowrap;
  text-align: center;
}

.dict-table-pinyin {
  border-left: 1px solid black;
  white-space:nowrap;
  text-align: center;
}

.dict-table-definition {
  border-left: 1px solid black;
  text-align: left;
  font-size: 50%;
}'''

class RubyPreview(QWebEngineView):
    def __init__(self):
        QWebEngineView.__init__(self)

    def render(self, ruby, entries=None):
        html_temp = '<html><head><style>{}</style><body lang="zh-Hans">{}{}</body></html>'
        entries = '' if entries is None else ('<br />' + entries)
        html = html_temp.format(CSS, ruby, entries)
        self.setHtml(html)
