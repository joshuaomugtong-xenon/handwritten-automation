from PyQt6.QtWidgets import (
    QComboBox,
)
from PyQt6.QtCore import (
    Qt,
)


class Dropdown(QComboBox):

    def __init__(
            self,
            parent=None,
            options: list[str] = None,
            current_index: int = 0,
            readonly: bool = False,
            width: int = 100
            ):

        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.addItems(options if options else [''])
        self.setCurrentIndex(current_index)
        self.setEditable(readonly)
        self.setFixedWidth(width)
        self.resize(self.sizeHint())
