from PyQt6.QtWidgets import (
    QSpinBox,
)
from PyQt6.QtCore import (
    Qt,
)


class IntegerInput(QSpinBox):

    def __init__(
            self,
            parent=None,
            minimum: int = 0,
            maximum: int = 10000,
            step: int = 1,
            value: int = 0,
            readonly: bool = False,
            buttons: bool = False,
            width: int = 120,
            ):

        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setSingleStep(step)
        self.setValue(value)
        self.setPrefix('')
        self.setSuffix('')
        self.setWrapping(False)
        self.setAccelerated(True)
        self.setReadOnly(readonly)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons if not buttons else QSpinBox.ButtonSymbols.UpDownArrows)
        self.setFixedWidth(width)
        self.resize(self.sizeHint())
