from PyQt6.QtWidgets import (
    QPushButton,
)
from PyQt6.QtCore import (
    Qt,
)


class Button(QPushButton):

    def __init__(self, text: str = ''):
        super().__init__(text, parent=None)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
