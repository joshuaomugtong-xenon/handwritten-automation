from PyQt6.QtWidgets import (
    QDoubleSpinBox,
)
from PyQt6.QtCore import (
    Qt,
)


class FloatInput(QDoubleSpinBox):

    def __init__(
            self,
            parent=None,
            minimum: float = 0.0,
            maximum: float = 100.0,
            step: float = 1.0,
            value: float = 0.0,
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
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons if not buttons else QDoubleSpinBox.ButtonSymbols.UpDownArrows)
        self.setFixedWidth(width)
        self.resize(self.sizeHint())
