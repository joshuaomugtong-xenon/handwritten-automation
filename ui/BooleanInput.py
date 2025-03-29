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


class BooleanInput(QLineEdit):
    def __init__(self, text: str = '', width: int = 120):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(width)
        yaml_bool_pattern = r"^(true|false|yes|no|on|off|y|n)$"
        self.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(yaml_bool_pattern, QRegularExpression.PatternOption.CaseInsensitiveOption)))
        self.setPlaceholderText('true, false, yes, no')

    def value(self) -> bool:
        return self.text().lower() in ['true', 'yes', 'on', 'y']
