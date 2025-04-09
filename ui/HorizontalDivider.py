from PyQt6.QtWidgets import (
    QFrame,
)
from PyQt6.QtCore import (
    Qt,
)


class HorizontalDivider(QFrame):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
