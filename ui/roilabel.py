from PyQt5.QtWidgets import (
    QLabel,
)
from PyQt5.QtGui import (
    QMouseEvent,
)
from PyQt5.QtCore import (
    Qt,
)
from typing import Callable


class ROILabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom_on_click: Callable = None
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if self.zoom_on_click:
            self.zoom_on_click()
        super().mousePressEvent(event)
