from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QCheckBox,
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
from .HorizontalDivider import HorizontalDivider


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

        # Homography Alignment
        # ------------------------

        layout.addWidget(QLabel('<h2>Homography Alignment</h2>'))
        layout.addWidget(HorizontalDivider())
        layout.addSpacing(10)

        frame = Frame()
        layout.addWidget(frame)
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        # Fiducial Enhancement (Morphological Closing)
        # ------------------------

        header_layout = QHBoxLayout()
        frame_layout.addLayout(header_layout)

        header_layout.addWidget(QLabel('<h3>Fiducial Enhancement</h3>'))
        self.enable_fiducial_enhancement = QCheckBox("Enable")
        self.enable_fiducial_enhancement.setChecked(True)
        header_layout.addWidget(self.enable_fiducial_enhancement)
        header_layout.addStretch(1)

        frame_layout.addWidget(QLabel('<i><font color="gray">(Morphological Closing)</font></i>'))
        frame_layout.addSpacing(5)

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
            width=90,
            buttons=True,
        )
        self.kernel_size_y = IntegerInput(
            minimum=1, maximum=100, value=3,
            width=90,
            buttons=True,
        )
        pair_layout = QHBoxLayout()
        pair_layout.addWidget(self.kernel_size_x)
        pair_layout.addWidget(self.kernel_size_y)
        pair_layout.addStretch(1)

        form_layout.addRow(QLabel('Kernel Size (x, y):'), pair_layout)

        self.iterations = IntegerInput(
            minimum=1, maximum=100, value=1,
            width=90,
            buttons=True,
        )
        form_layout.addRow(QLabel('Iterations:'), self.iterations)

        frame = Frame()
        layout.addWidget(frame)
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        # Brightness and Contrast
        # ------------------------

        header_layout = QHBoxLayout()
        frame_layout.addLayout(header_layout)

        header_layout.addWidget(QLabel('<h3>Brightness and Contrast</h3>'))
        self.enable_brightness_contrast = QCheckBox("Enable")
        self.enable_brightness_contrast.setChecked(True)
        header_layout.addWidget(self.enable_brightness_contrast)
        header_layout.addStretch(1)

        frame_layout.addSpacing(5)

        form_layout = QFormLayout()
        frame_layout.addLayout(form_layout)

        self.alpha = FloatInput(
            minimum=1.0, maximum=3.0, value=1.5, step=0.1,
            width=90,
            buttons=True,
        )
        form_layout.addRow(QLabel('Alpha (Brightness):'), self.alpha)

        self.beta = FloatInput(
            minimum=0.0, maximum=100.0, value=10.0, step=1.0,
            width=90,
            buttons=True,
        )
        form_layout.addRow(QLabel('Beta (Contrast):'), self.beta)

        # Data Extraction
        # ------------------------

        layout.addWidget(QLabel('<h2>Data Extraction</h2>'))
        layout.addWidget(HorizontalDivider())
        layout.addSpacing(10)

        # Image Denoising (Fast Non-Local Means Denoising)
        # ------------------------

        frame = Frame()
        layout.addWidget(frame)

        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        header_layout = QHBoxLayout()
        frame_layout.addLayout(header_layout)

        header_layout.addWidget(QLabel('<h3>Image Denoising</h3>'))
        self.enable_denoising = QCheckBox("Enable")
        self.enable_denoising.setChecked(True)
        header_layout.addWidget(self.enable_denoising)
        header_layout.addStretch(1)

        frame_layout.addWidget(QLabel('<i><font color="gray">(Fast Non-Local Means Denoising)</font></i>'))
        frame_layout.addSpacing(5)

        form_layout = QFormLayout()
        frame_layout.addLayout(form_layout)
        frame_layout.addSpacing(5)

        self.filter_strength = FloatInput(
            minimum=0.01, maximum=100.00, value=10.00, step=0.01,
            width=90,
            buttons=True,
        )
        form_layout.addRow(QLabel('Filter Strength:'), self.filter_strength)

        self.template_window_size = IntegerInput(
            minimum=1, maximum=99, value=7, step=2,
            width=90,
            buttons=True,
        )
        form_layout.addRow(QLabel('Template Window Size:'), self.template_window_size)

        self.search_window_size = IntegerInput(
            minimum=1, maximum=99, value=21, step=2,
            width=90,
            buttons=True,
        )
        form_layout.addRow(QLabel('Search Window Size:'), self.search_window_size)

        # Contrast Enhancement (CLAHE)
        # ------------------------

        frame = Frame()
        layout.addWidget(frame)

        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        header_layout = QHBoxLayout()
        frame_layout.addLayout(header_layout)

        header_layout.addWidget(QLabel('<h3>Contrast Enhancement</h3>'))
        self.enable_clahe = QCheckBox("Enable")
        self.enable_clahe.setChecked(False)
        header_layout.addWidget(self.enable_clahe)
        header_layout.addStretch(1)

        frame_layout.addWidget(QLabel('<i><font color="gray">(Contrast Limited Adaptive Histogram Equalization)</font></i>'))
        frame_layout.addSpacing(5)

        form_layout = QFormLayout()
        frame_layout.addLayout(form_layout)

        self.clip_limit = FloatInput(
            minimum=0.01, maximum=100.00, value=40.00, step=0.01,
            width=90,
            buttons=True,
        )
        form_layout.addRow(QLabel('Clip Limit:'), self.clip_limit)

        self.tile_grid_size_x = IntegerInput(
            minimum=1, maximum=100, value=8, step=2,
            width=90,
            buttons=True,
        )
        self.tile_grid_size_y = IntegerInput(
            minimum=1, maximum=100, value=8, step=2,
            width=90,
            buttons=True,
        )
        pair_layout = QHBoxLayout()
        pair_layout.addWidget(self.tile_grid_size_x)
        pair_layout.addWidget(self.tile_grid_size_y)
        pair_layout.addStretch(1)
        form_layout.addRow(QLabel('Tile Grid Size (x, y):'), pair_layout)

        layout.addStretch(1)

    def apply_data_extraction_preprocessing(self, image: MatLike) -> MatLike:

        image = image.copy()

        # Denoising (Fast Non-Local Means Denoising)
        # ------------------------

        if self.enable_denoising.isChecked():
            h = self.filter_strength.value()
            template_window_size = self.template_window_size.value()
            template_window_size = template_window_size if template_window_size % 2 == 1 else template_window_size + 1
            search_window_size = self.search_window_size.value()
            search_window_size = search_window_size if search_window_size % 2 == 1 else search_window_size + 1
            image = cv2.fastNlMeansDenoisingColored(
                src=image,
                h=h,
                templateWindowSize=template_window_size,
                searchWindowSize=search_window_size)

        # Contrast Enhancement (CLAHE)
        # ------------------------

        if self.enable_clahe.isChecked():
            clip_limit = self.clip_limit.value()
            tile_grid_size = (self.tile_grid_size_x.value(), self.tile_grid_size_y.value())

            clahe = cv2.createCLAHE(
                clipLimit=clip_limit,
                tileGridSize=tile_grid_size)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = clahe.apply(image)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image

    def apply_homography_preprocessing(self, image: MatLike) -> MatLike:

        image = image.copy()

        # Morphological Closing
        # ------------------------
        if self.enable_fiducial_enhancement.isChecked():
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
        if self.enable_brightness_contrast.isChecked():
            alpha = self.alpha.value()
            beta = self.beta.value()
            image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        return image
