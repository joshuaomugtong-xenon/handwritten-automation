from PyQt6.QtWidgets import (
    QLabel,
)
from PyQt6.QtCore import (
    Qt,
)


class Label(QLabel):
    def __init__(self, text: str = ''):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
