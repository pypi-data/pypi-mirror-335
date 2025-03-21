import pygments
from finesse.script.highlighter import KatScriptPygmentsLexer
from pygments.formatters import HtmlFormatter
from PySide6 import QtCore, QtWidgets

import virgui


class KatScriptViewer(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.header = QtWidgets.QLabel(
            text="# Current KatScript",
            textFormat=QtCore.Qt.TextFormat.MarkdownText,
        )
        self.text_browser = QtWidgets.QTextBrowser()
        self.layout().addWidget(self.header)
        self.layout().addWidget(self.text_browser)
        self.update()

    @QtCore.Slot()
    def update(self):
        kat = virgui.GLOBAL_MODEL.unparse()
        # this line is too long to render nicely
        # maybe https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTextEdit.html#PySide6.QtWidgets.QTextEdit.lineWrapMode
        kat = kat.replace(
            "# Items below could not be matched to original script, or were not present when the model was originally parsed.",
            "# Items below could not be matched to original script,\n# or were not present when the model was originally parsed."
            "",
        )
        html = pygments.highlight(
            kat,
            KatScriptPygmentsLexer(),
            HtmlFormatter(
                nobackground=True, noclasses=True, cssstyles="font-size: large"
            ),
        )
        self.text_browser.setHtml(html)
