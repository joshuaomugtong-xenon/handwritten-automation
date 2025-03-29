from PyQt6.QtWidgets import (
    QLabel,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text: str = ''):
        super().__init__(text, parent=None)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
