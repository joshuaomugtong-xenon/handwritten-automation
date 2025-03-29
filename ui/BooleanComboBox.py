from PyQt6.QtWidgets import (
    QComboBox,
)
from PyQt6.QtCore import (
    Qt,
)


class BooleanComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(['Yes', 'No'])
        self.setCurrentIndex(0)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(100)
        self.resize(self.sizeHint())

    def value(self) -> bool:
        return self.currentText() == 'Yes'
