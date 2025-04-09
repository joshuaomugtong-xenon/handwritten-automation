from PyQt6.QtWidgets import (
    QFrame,
)

from PyQt6.QtCore import (
    Qt,
)


class Frame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        self.setStyleSheet(
            "QFrame[selected=true] { background-color: rgba(135, 206, 250, 0); "
            "border: 2px solid #4682B4; border-radius: 5px; }"
        )
