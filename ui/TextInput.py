from PyQt6.QtWidgets import (
    QLineEdit,
)
from PyQt6.QtCore import (
    Qt,
)


class TextInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 500):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        self.setPlaceholderText('Enter text')

    def value(self) -> str:
        return self.text()
