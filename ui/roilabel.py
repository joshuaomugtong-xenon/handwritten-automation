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
        self._onclick_func: Callable = None
        self.setCursor(Qt.PointingHandCursor)

    def setOnClick(self, func: Callable):
        self._onclick_func = func

    def mousePressEvent(self, event: QMouseEvent):
        if self._onclick_func:
            self._onclick_func()
        super().mousePressEvent(event)
