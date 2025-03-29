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


class PositiveIntegerInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 120):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        pattern = r"^([0-9]|[1-9][0-9]|[1-9][0-9]{2}|[1-9][0-9]{3}|10000)$"
        self.setValidator(
            QRegularExpressionValidator(QRegularExpression(pattern)))
        self.setPlaceholderText('0-10000')

    def value(self) -> int:
        return int(self.text())
