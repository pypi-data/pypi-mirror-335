from finesse.parameter import Parameter
from PySide6 import QtCore, QtWidgets


class KatScriptLog(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.header = QtWidgets.QLabel(
            text="# Change Log",
            textFormat=QtCore.Qt.TextFormat.MarkdownText,
        )
        self.log_text_edit = QtWidgets.QTextEdit()
        self.layout().addWidget(self.header)
        self.layout().addWidget(self.log_text_edit)

    @QtCore.Slot()
    def update(self, parameter: Parameter, old_val: float, new_val: float):
        self.log_text_edit.append(f"{parameter.full_name}: {old_val} -> {new_val}")
