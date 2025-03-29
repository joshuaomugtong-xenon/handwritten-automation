from PyQt6.QtWidgets import (
    QLineEdit,
)
from PyQt6.QtGui import (
    QRegularExpressionValidator,
)
from PyQt6.QtCore import (
    Qt,
    QRegularExpression,
)


class TypeInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 500):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        pattern = r"^(text|encirclement|checkbox)$"
        self.setValidator(
            QRegularExpressionValidator(QRegularExpression(pattern)))
        self.setPlaceholderText('text, encirclement, checkbox')

    def value(self) -> str:
        return self.text()
