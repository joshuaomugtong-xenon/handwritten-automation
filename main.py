import os
import sys
import yaml
import json
import cv2
import qdarkstyle
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QComboBox,
    QLineEdit,
    QLabel,
    QDialog,
    QSpacerItem,
    QSizePolicy,
    QLayout,
    QFileDialog,
    QSplitter,
)
from PyQt5.QtGui import (
    QPixmap,
    QImage,
)
from PyQt5.QtCore import Qt

from preproc import (
    ROIExtractor,
    HomographyAligner,
)
from ui import (
    PhotoViewer,
    OpenFileDialog,
)

MatLike = cv2.typing.MatLike


class ProjectApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_title = 'Project'

        self.accepted_image_types = ['.jpg', '.jpeg', '.png']

        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

        self.roi_extractor = ROIExtractor(detector)
        self.homography_aligner = HomographyAligner(detector)
        self.datafields = {}

        self.templates = {}
        self.templates_folder = 'templates'
        self.scanned_folder = 'scanned'
        self.data_folder = 'data'
        self.load_templates()
        self.current_image_path = ''

        self.initUI()
        self.showMaximized()

    def initUI(self):
        self.setWindowTitle(self.app_title)
        self.setGeometry(100, 100, 1600, 900)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')

        new_action = file_menu.addAction('&New')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.reset_datafields)

        open_action = file_menu.addAction('&Open...')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.show_file_dialog)

        save_action = file_menu.addAction('&Save...')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_data)

        close_action = file_menu.addAction('&Exit')
        close_action.triggered.connect(self.close)

        self.main_widget = QSplitter(Qt.Horizontal)

        self.photo_viewer = PhotoViewer(self)
        self.main_widget.addWidget(self.photo_viewer)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.main_widget.addWidget(scroll_area)

        self.data_widget = QWidget()
        self.data_widget_layout = QVBoxLayout()
        self.data_widget_layout.setContentsMargins(20, 20, 20, 20)
        self.data_widget.setLayout(self.data_widget_layout)
        scroll_area.setWidget(self.data_widget)

        self.setCentralWidget(self.main_widget)
        self.main_widget.setSizes([self.width() // 2, self.width() // 2])

    def show_file_dialog(self):
        dialog = OpenFileDialog(self)
        if dialog.exec() == QDialog.Accepted:
            image_path, selected = dialog.get_selected_files()

            try:
                self.process_image(image_path, selected)
            except Exception as e:
                print(f'Image process failed: {e}')

    def process_image(self, image_path, selected):
        self.reset_datafields()
        self.current_image_path = image_path

        template: dict = self.templates[selected]
        length = template.get('length')
        width = template.get('width')

        image = cv2.imread(image_path)

        try:
            image = self.homography_aligner.align(image, length, width)
        except Exception as e:
            print(f'Failed to align image: {e}')
            return

        disp_image = image.copy()
        loc = self.roi_extractor.get_marker_locations(image)
        self.centers, self.corners = loc
        self.roi_extractor.draw_markers(disp_image, self.centers, self.corners)

        regions: list[dict] = template.get('regions')
        for region in regions:
            markers = region.get('markers')
            image_layout = QHBoxLayout()
            roi_image = QLabel()
            roi_image.setAttribute(Qt.WA_DeleteOnClose)
            try:
                self.roi_extractor.draw_roi(disp_image, self.centers, *markers)
                cropped_roi = self.roi_extractor.crop_roi(
                    image, self.centers, *markers)
                pixmap = QPixmap.fromImage(create_image(cropped_roi))
                roi_image.setPixmap(pixmap)
            except Exception as e:
                print(f'Failed to identify region: {e}')
            image_layout.addSpacing(20)
            image_layout.addWidget(roi_image)

            region_name = region.get('name')
            label_widget = QLabel(text=region_name)
            label_widget.setAttribute(Qt.WA_DeleteOnClose)

            field_layout = QHBoxLayout()
            field_layout.addSpacing(20)
            region_type = region.get('type')

            if region_type == 'encirclement' or region_type == 'checkbox':
                field_widget = QComboBox()
                field_widget.setAttribute(Qt.WA_DeleteOnClose)
                field_widget.setSizeAdjustPolicy(QComboBox.AdjustToContents)
                field_widget.addItems(['Yes', 'No'])
                field_widget.setMinimumContentsLength(10)
                field_layout.addWidget(field_widget)
                spacer = QSpacerItem(
                    2000, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
                field_layout.addSpacerItem(spacer)
            else:
                field_widget = QLineEdit()
                field_widget.setAttribute(Qt.WA_DeleteOnClose)
                field_layout.addWidget(field_widget)

            self.datafields[region_name] = field_widget

            self.data_widget_layout.addWidget(label_widget)
            self.data_widget_layout.addLayout(field_layout)
            self.data_widget_layout.addLayout(image_layout)
            self.data_widget_layout.addSpacing(20)

        pixmap = QPixmap.fromImage(create_image(disp_image))
        self.photo_viewer.setPhoto(pixmap)

    def save_data(self):
        if self.datafields == {}:
            return
        data = {}
        for region_name, field_widget in self.datafields.items():
            if isinstance(field_widget, QLineEdit):
                data[region_name] = field_widget.text()
            elif isinstance(field_widget, QComboBox):
                data_ = field_widget.currentText()
                data[region_name] = True if data_ == 'Yes' else False
            else:
                print(f'Unhandled widget type for region_name: {region_name}')

        base_name = os.path.basename(self.current_image_path)
        filename = os.path.splitext(base_name)[0]
        default_save_name = f"{filename}.json"
        save_path = os.path.join(self.data_folder, default_save_name)

        save_path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save',
            directory=save_path,
            filter='JSON Files (*.json)',
        )

        if save_path:
            try:
                with open(save_path, 'w') as file:
                    json.dump(data, file, indent=4)
                print(f'Data saved to {save_path}')
            except Exception as e:
                print(f'Failed to save data: {e}')

    def reset_datafields(self):
        self.datafields = {}
        self.photo_viewer.setPhoto(None)
        self.clear_layout(self.data_widget_layout)

    def clear_layout(self, layout: QLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)
                    child_layout.deleteLater()

    def load_templates(self):
        self.templates = {}
        paths = []
        try:
            dir_list = os.listdir(self.templates_folder)
            for file in dir_list:
                path = os.path.join(self.templates_folder, file)
                if os.path.isfile(path) and file.endswith('.yaml'):
                    paths.append(path)
        except Exception as e:
            print(f'Error reading folder: {e}')

        for path in paths:
            try:
                with open(path, 'r') as file:
                    template: dict = yaml.safe_load(file)
                form_type = template.get('form_type')
                form_title = template.get('form_title')
                type_ = f'{form_type} - {form_title}'
                # To do: INPUT VALIDATION
                self.templates[type_] = template
            except Exception as e:
                print(f'Error parsing YAML file: {e}')
                continue


def create_image(image: MatLike) -> QImage:
    height, width, channel = image.shape
    bytes_per_line = channel * width
    return QImage(
        image.data,
        width, height, bytes_per_line,
        QImage.Format_BGR888
    )


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    from PyQt5.QtGui import QFont
    font = QFont()
    font.setPixelSize(14)
    app.setFont(font)
    window = ProjectApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
