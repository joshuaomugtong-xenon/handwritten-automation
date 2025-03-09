import traceback

from PyQt5.QtWidgets import (
    QMessageBox, QTextEdit
)


class ErrorDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        traceback_text = traceback.format_exc()
        self.setWindowTitle("Error Occurred")

        self.traceback_edit = QTextEdit()
        self.traceback_edit.setReadOnly(True)
        self.traceback_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.traceback_edit.setText(traceback_text)
        self.traceback_edit.setMinimumWidth(600)
        self.traceback_edit.setMinimumHeight(300)

        layout = self.layout()
        layout.addWidget(self.traceback_edit, 1, 0, 1, layout.columnCount())

        self.setStandardButtons(QMessageBox.Ok)
        self.exec()
