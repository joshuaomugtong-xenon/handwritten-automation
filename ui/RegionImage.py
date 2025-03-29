from PyQt6.QtWidgets import (
    QLabel,
)
from PyQt6.QtGui import (
    QMouseEvent,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)


class RegionImage(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(event)
