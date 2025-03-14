import os
import sys
import json
import cv2
from cv2.typing import MatLike
import qdarkstyle
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QComboBox,
    QLineEdit,
    QDialog,
    QLayout,
    QFileDialog,
    QSplitter,
    QGroupBox,
    QTabWidget,
    QTextEdit,
)
from PyQt5.QtGui import (
    QPixmap,
    QImage,
    QFont,
)
from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
)
from modules import (
    ROIExtractor,
    HomographyAligner,
    CheckboxDetector,
    EncirclementDetector,
    TextRecognizer,
    validate_template_file,
    Template,
    RegionType,
)
from ui import (
    PhotoViewerWidget,
    OpenFileDialog,
    ErrorDialog,
    ROILabel,
    ROIRectItem,
)


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
        self.checkbox_detector = CheckboxDetector()
        self.encirclement_detector = EncirclementDetector()
        self.text_recognizer = TextRecognizer()

        self.datafields = {}

        self.templates: dict[str, Template] = {}
        self.templates_folder = 'templates'
        self.scanned_folder = 'scanned'
        self.data_folder = 'data'
        self.load_templates()
        self.current_image_path = ''
        self.selected_template = ''

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

        edit_menu = menu_bar.addMenu('&Edit')

        reload_action = edit_menu.addAction('&Reload')
        reload_action.setShortcut('Ctrl+R')
        reload_action.triggered.connect(self.reload_data)

        self.main_widget = QSplitter(Qt.Horizontal)

        self.photo_viewer = PhotoViewerWidget(self)
        self.main_widget.addWidget(self.photo_viewer)

        self.right_tab_widget = QTabWidget()
        self.main_widget.addWidget(self.right_tab_widget)

        self.data_scroll_area = QScrollArea()
        self.data_scroll_area.setWidgetResizable(True)
        self.right_tab_widget.addTab(self.data_scroll_area, 'Data')

        self.data_widget = QWidget()
        self.data_widget_layout = QVBoxLayout()
        self.data_widget_layout.setContentsMargins(20, 20, 20, 20)
        self.data_widget.setLayout(self.data_widget_layout)
        self.data_scroll_area.setWidget(self.data_widget)

        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont('Courier New', 12))
        self.text_editor.setLineWrapMode(QTextEdit.NoWrap)

        self.right_tab_widget.addTab(self.text_editor, 'Template')

        self.setCentralWidget(self.main_widget)
        self.main_widget.setSizes([self.width() // 2, self.width() // 2])

    def show_file_dialog(self):
        dialog = OpenFileDialog(self)
        if dialog.exec() == QDialog.Accepted:
            image_path, selected = dialog.get_selected_files()
            try:
                self.process_image(image_path, selected)
            except Exception:
                ErrorDialog()

    def reload_data(self):
        if self.current_image_path == '' or self.selected_template == '':
            return
        self.load_templates()
        self.process_image(self.current_image_path, self.selected_template)

    def process_image(self, image_path, selected):
        self.reset_datafields()
        self.current_image_path = image_path
        self.selected_template = selected

        template = self.templates[selected]
        length = template.length
        width = template.width

        image = cv2.imread(image_path)
        image = self.homography_aligner.align(image, length, width)

        pixmap = QPixmap.fromImage(create_image(image))
        self.photo_viewer.viewer.setPhoto(pixmap)

        regions = template.regions

        if template.use_coordinates:
            pass
        else:
            centers, corners = self.roi_extractor.get_marker_locations(image)
            for _, corner in corners.items():
                ((x1, y1), _, (x2, y2), _) = corner
                self.add_rect(x1, y1, x2, y2)

        for region in regions:
            coordinates = []
            if template.use_coordinates:
                coordinates = region.coordinates
            else:
                try:
                    markers = region.markers
                    coordinates = markers_to_coordinates(markers, centers)
                except Exception as e:
                    print(f'Failed to identify region: {e}')

            # Draw the ROI
            rect_item = self.add_rect(*coordinates)

            def create_scroll_on_click(
                    widget: ProjectApp,
                    groupbox: QGroupBox):
                def callback():
                    widget.scroll_to_widget(groupbox)
                return callback

            # Crop the ROI
            cropped_roi = self.roi_extractor.crop_roi_coordinates(
                image, *coordinates)

            def create_zoom_onclick(
                    widget: ProjectApp,
                    rect_item: ROIRectItem):
                def callback():
                    widget.photo_viewer.viewer.zoomToRect(
                        rect_item.rect())
                    rect_item.setSelected(True)
                    widget.photo_viewer.viewer._scene.update()
                return callback

            # Display the ROI under the label
            pixmap = QPixmap.fromImage(create_image(cropped_roi))
            roi_image = ROILabel()
            roi_image.setAttribute(Qt.WA_DeleteOnClose)
            roi_image.setPixmap(pixmap)
            roi_image.zoom_on_click = create_zoom_onclick(self, rect_item)

            groupbox = QGroupBox(region.name)
            groupbox.setAttribute(Qt.WA_DeleteOnClose)
            groupbox_layout = QVBoxLayout()
            groupbox.setLayout(groupbox_layout)

            groupbox_layout.addSpacing(20)

            rect_item.scroll_on_click = create_scroll_on_click(self, groupbox)

            if region.type == RegionType.ENCIRCLEMENT or \
                    region.type == RegionType.CHECKBOX:
                field_widget = QComboBox()
                field_widget.setAttribute(Qt.WA_DeleteOnClose)
                # field_widget.setSizeAdjustPolicy(QComboBox.AdjustToContents)
                field_widget.addItems(['Yes', 'No'])
                field_widget.setFixedWidth(100)
                field_widget.resize(field_widget.sizeHint())
                # field_widget.setMinimumContentsLength(10)
                groupbox_layout.addWidget(field_widget)
            elif region.type == 'text':
                field_widget = QLineEdit()
                field_widget.setFixedWidth(500)
                field_widget.setAlignment(Qt.AlignLeft)
                field_widget.setAttribute(Qt.WA_DeleteOnClose)
                groupbox_layout.addWidget(field_widget)
            else:
                print(f'Unknown region type: \'{region.type}\'')

            gray_roi = cv2.cvtColor(cropped_roi, cv2.COLOR_BGR2GRAY)
            if region.type == 'encirclement':
                has_circle = self.encirclement_detector.detect(gray_roi)
                field_widget.setCurrentIndex(0 if has_circle else 1)
            elif region.type == 'checkbox':
                is_checked = self.checkbox_detector.detect(gray_roi)
                field_widget.setCurrentIndex(0 if is_checked else 1)
            elif region.type == 'text':
                text = self.text_recognizer.recognize_text(cropped_roi)
                field_widget.setText(text)
            else:
                print(f'Unknown region type: \'{region.type}\'')

            groupbox_layout.addWidget(roi_image)
            groupbox_layout.addSpacing(20)

            self.datafields[region.name] = field_widget

            self.data_widget_layout.addWidget(groupbox)
            self.data_widget_layout.addSpacing(20)

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
            except Exception:
                ErrorDialog()

    def reset_datafields(self):
        self.datafields = {}
        self.photo_viewer.viewer.setPhoto(None)
        self.clear_layout(self.data_widget_layout)
        self.current_image_path = ''
        self.selected_template = ''
        self.clear_rects()

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

    def scroll_to_widget(self, widget: QWidget):
        vertical_scroll_bar = self.data_scroll_area.verticalScrollBar()
        widget_pos = widget.mapTo(
            self.data_widget, widget.rect().topLeft())

        # Create animation for vertical scrollbar
        self.data_animation = QPropertyAnimation(vertical_scroll_bar, b'value')
        self.data_animation.setDuration(300)
        self.data_animation.setStartValue(vertical_scroll_bar.value())
        self.data_animation.setEndValue(widget_pos.y())
        self.data_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Start the animation
        self.data_animation.start()

    def load_templates(self):
        self.templates = {}

        try:
            # Get all YAML files in the template folder
            template_files = Path(self.templates_folder).rglob('*.yaml')

            for template_file in template_files:
                try:
                    # Validate the template
                    template = validate_template_file(template_file)

                    # Add the template to the dictionary
                    name = f'{template.form_type} - {template.form_title}'
                    self.templates[name] = template
                except Exception:
                    ErrorDialog()
        except Exception:
            ErrorDialog()

    def add_rect(
            self,
            x1: int,
            y1: int,
            x2: int,
            y2: int,
            ) -> ROIRectItem:

        rect_item = ROIRectItem(x1, y1, x2 - x1, y2 - y1)
        self.photo_viewer.viewer._scene.addItem(rect_item)
        return rect_item

    def clear_rects(self):
        for item in self.photo_viewer.viewer._scene.items():
            if isinstance(item, ROIRectItem):
                self.photo_viewer.viewer._scene.removeItem(item)


Point = tuple[int, int]


def markers_to_coordinates(
        markers: list[int],
        centers: dict[int, Point]
        ) -> list[int]:

    assert len(markers) == 4
    x1_id, x2_id, y1_id, y2_id = markers

    a = centers[x1_id][0]
    h = centers[x2_id][0]
    b = centers[y1_id][1]
    k = centers[y2_id][1]

    return [
        min(a, h),
        min(b, k),
        max(a, h),
        max(b, k),
    ]


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
