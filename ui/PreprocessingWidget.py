from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
)
from PyQt6.QtCore import (
    Qt,
)
import cv2

from .utils import MatLike

from .Frame import Frame
from .Dropdown import Dropdown
from .IntegerInput import IntegerInput
from .FloatInput import FloatInput


class PreprocessingWidget(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.init_ui()

    def init_ui(self):

        outer_layout = QHBoxLayout()
        self.setLayout(outer_layout)

        layout = QVBoxLayout()
        outer_layout.addLayout(layout)
        outer_layout.addStretch(1)

        # Morphological Closing
        # ------------------------

        frame = Frame()
        layout.addWidget(frame)
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        frame_layout.addWidget(QLabel('<h3>Morphological Closing</h3>'))
        frame_layout.addSpacing(5)

        frame_layout.addWidget(QLabel('<b>Structuring Element</b>'))

        form_layout = QFormLayout()
        frame_layout.addLayout(form_layout)

        self.kernel_shape = Dropdown(
            options=['Rectangular', 'Elliptical', 'Cross-shaped'],
            current_index=0,
            width=150,
        )
        form_layout.addRow(QLabel('Kernel Shape:'), self.kernel_shape)

        self.kernel_size_x = IntegerInput(
            minimum=1, maximum=100, value=3,
            width=75,
            buttons=True,
        )
        self.kernel_size_y = IntegerInput(
            minimum=1, maximum=100, value=3,
            width=75,
            buttons=True,
        )
        pair_layout = QHBoxLayout()
        pair_layout.addWidget(QLabel('X:'))
        pair_layout.addWidget(self.kernel_size_x)
        pair_layout.addWidget(QLabel('Y:'))
        pair_layout.addWidget(self.kernel_size_y)
        pair_layout.addStretch(1)

        form_layout.addRow(QLabel('Kernel Size:'), pair_layout)

        self.iterations = IntegerInput(
            minimum=1, maximum=100, value=1,
            width=75,
            buttons=True,
        )
        form_layout.addRow(QLabel('Iterations:'), self.iterations)

        frame = Frame()
        layout.addWidget(frame)
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        frame_layout.addWidget(QLabel('<h3>Brightness and Contrast</h3>'))
        frame_layout.addSpacing(5)

        frame_layout.addWidget(QLabel('<b>Brightness</b>'))

        form_layout = QFormLayout()
        frame_layout.addLayout(form_layout)

        self.alpha = FloatInput(
            minimum=1.0, maximum=3.0, value=1.5, step=0.1,
            width=75,
            buttons=True,
        )
        form_layout.addRow(QLabel('Alpha:'), self.alpha)

        frame_layout.addWidget(QLabel('<b>Contrast</b>'))

        form_layout = QFormLayout()
        frame_layout.addLayout(form_layout)

        self.beta = FloatInput(
            minimum=0.0, maximum=100.0, value=10.0, step=1.0,
            width=75,
            buttons=True,
        )
        form_layout.addRow(QLabel('Beta:'), self.beta)

        layout.addStretch(1)

    def apply_preprocessing(self, image: MatLike) -> MatLike:

        # Morphological Closing
        # ------------------------

        image = image.copy()
        match self.kernel_shape.currentText():
            case 'Rectangular':
                kernel_shape = cv2.MORPH_RECT
            case 'Elliptical':
                kernel_shape = cv2.MORPH_ELLIPSE
            case 'Cross-shaped':
                kernel_shape = cv2.MORPH_CROSS
            case _:
                kernel_shape = cv2.MORPH_RECT
        kernel_size = (self.kernel_size_x.value(), self.kernel_size_y.value())
        iterations = self.iterations.value()

        structuring_element = cv2.getStructuringElement(
            shape=kernel_shape,
            ksize=kernel_size)
        image = cv2.morphologyEx(
            src=image, op=cv2.MORPH_CLOSE, kernel=structuring_element, iterations=iterations)

        # Brightness and Contrast
        # ------------------------

        alpha = self.alpha.value()
        beta = self.beta.value()

        image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        return image
