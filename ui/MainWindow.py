from __future__ import annotations
import os

import json
import cv2
import yaml
from cv2.typing import MatLike
from pathlib import Path
from PyQt6.QtWidgets import (
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
    QLabel,
)
from PyQt6.QtGui import (
    QPixmap,
    QImage,
)
from PyQt6.QtCore import (
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
from modules.config import (
    TEMPLATES_FOLDER,
    DATA_FOLDER,
)

from .ErrorDialog import ErrorDialog
from .OpenFileDialog import OpenFileDialog
from .PhotoViewer import PhotoViewerWidget
from .ROILabel import ROILabel
from .ROIRectItem import ROIRectItem
from .TemplateEditor import TemplateWidget, PositiveIntegerInput


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_title = 'Project'

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
        self.load_templates()
        self.current_image_path = ''
        self.selected_template = ''

        self.template_fields: dict[str, QLineEdit] = {}
        self.template_regions: list[dict[str, QLineEdit | list[QLineEdit]]] = [] # noqa

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

        save_template_action = file_menu.addAction('Save Template...')
        save_template_action.setShortcut('Ctrl+Shift+S')
        save_template_action.triggered.connect(self.save_template)

        close_action = file_menu.addAction('&Exit')
        close_action.triggered.connect(self.close)

        edit_menu = menu_bar.addMenu('&Edit')

        reload_action = edit_menu.addAction('&Reload')
        reload_action.setShortcut('Ctrl+R')
        reload_action.triggered.connect(self.reload_data)

        self.main_widget = QSplitter(Qt.Orientation.Horizontal)

        self.photo_viewer = PhotoViewerWidget(self)
        self.photo_viewer.viewer.owner = self
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

        self.template_editor = TemplateWidget()
        self.template_scroll_area = QScrollArea()
        self.template_scroll_area.setWidgetResizable(True)
        self.template_scroll_area.setWidget(self.template_editor)
        # Disable horizontal scrollbar
        self.template_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.right_tab_widget.addTab(self.template_scroll_area, 'Template')

        self.setCentralWidget(self.main_widget)
        self.main_widget.setSizes([self.width() // 2, self.width() // 2])

    def show_file_dialog(self):
        dialog = OpenFileDialog(self)
        self.load_templates()
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        self.template_fields = self.template_editor.init_ui(template)

        image = cv2.imread(image_path)
        image = self.homography_aligner.align(image, length, width)

        pixmap = QPixmap.fromImage(create_image(image))
        self.photo_viewer.viewer.set_photo(pixmap)

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
                coordinates = markers_to_coordinates(region.markers, centers)

            # Draw the ROI
            rect_item = self.add_rect(*coordinates)

            # Crop the ROI
            cropped_roi = self.roi_extractor.crop_roi_coordinates(
                image, *coordinates)

            def create_zoom_onclick(
                    widget: MainWindow,
                    rect_item: ROIRectItem):
                def callback():
                    widget.photo_viewer.viewer.zoom_to_rect(
                        rect_item.rect())
                    rect_item.setSelected(True)
                    widget.photo_viewer.viewer._scene.update()
                return callback

            # Display the ROI under the label
            pixmap = QPixmap.fromImage(create_image(cropped_roi))
            roi_image = ROILabel()
            roi_image.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            roi_image.setPixmap(pixmap)
            # When the ROI image is click on the data tab, it will zoom
            # to the ROI on the photo viewer
            roi_image.zoom_on_click = create_zoom_onclick(self, rect_item)

            # Add the region to the template regions
            ui_handles, tp_groupbox, link = self.template_editor.add_region(
                region,
                template.use_coordinates)

            # Store the region handles so we can save it
            self.template_regions.append(ui_handles)

            # Store the rect_item so we can zoom to it
            if link:
                link.owner = self
                link.rect_item = rect_item

            x1, y1, x2, y2 = None, None, None, None
            if template.use_coordinates:
                x1, y1, x2, y2 = ui_handles['coordinates']

            # Define the data groupbox first so the rect_item can scroll to it
            groupbox = QGroupBox(region.name)
            groupbox.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            groupbox_layout = QVBoxLayout()
            groupbox.setLayout(groupbox_layout)
            groupbox_layout.addSpacing(20)

            # When the ROI is resized, it will update the coordinates on the
            # template editor
            rect_item.x1 = x1
            rect_item.y1 = y1
            rect_item.x2 = x2
            rect_item.y2 = y2

            # Store the parent widget so we can call parent functions
            # from it
            rect_item.owner = self
            # Store the template region so we can scroll to it
            # and delete it later
            rect_item.template_groupbox = tp_groupbox
            # Store the data groupbox so we can scroll to it
            rect_item.data_groupbox = groupbox

            value_label = QLabel('Value:')
            value_label.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            groupbox_layout.addWidget(value_label)
            if region.type == RegionType.ENCIRCLEMENT or \
                    region.type == RegionType.CHECKBOX:
                field_widget = QComboBox()
                field_widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                # field_widget.setSizeAdjustPolicy(QComboBox.AdjustToContents)
                field_widget.addItems(['Yes', 'No'])
                field_widget.setFixedWidth(100)
                field_widget.resize(field_widget.sizeHint())
                # field_widget.setMinimumContentsLength(10)
                groupbox_layout.addWidget(field_widget)
            elif region.type == 'text':
                field_widget = QLineEdit()
                field_widget.setFixedWidth(500)
                field_widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
                field_widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
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

            roi_label = QLabel('Image:')
            roi_label.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            roi_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            groupbox_layout.addWidget(roi_label)

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
        save_path = os.path.join(DATA_FOLDER, default_save_name)

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
        self.datafields.clear()
        self.photo_viewer.viewer.set_photo(None)
        self.clear_layout(self.data_widget_layout)
        self.current_image_path = ''
        self.selected_template = ''
        self.clear_rects()
        self.template_editor.reset_layout()
        self.template_fields.clear()
        self.template_regions.clear()

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

    def scroll_to_data_groupbox(self, widget: QWidget):
        vertical_scroll_bar = self.data_scroll_area.verticalScrollBar()
        widget_pos = widget.mapTo(
            self.data_widget, widget.rect().topLeft())

        # Create animation for vertical scrollbar
        self.data_animation = QPropertyAnimation(vertical_scroll_bar, b'value')
        self.data_animation.setDuration(300)
        self.data_animation.setStartValue(vertical_scroll_bar.value())
        self.data_animation.setEndValue(widget_pos.y())
        self.data_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Start the animation
        self.data_animation.start()

    def scroll_to_template_groupbox(self, widget: QWidget):
        vertical_scroll_bar = self.template_scroll_area.verticalScrollBar()
        widget_pos = widget.mapTo(
            self.template_editor, widget.rect().topLeft())

        # Create animation for vertical scrollbar
        self.temp_animation = QPropertyAnimation(vertical_scroll_bar, b'value')
        self.temp_animation.setDuration(300)
        self.temp_animation.setStartValue(vertical_scroll_bar.value())
        self.temp_animation.setEndValue(widget_pos.y())
        self.temp_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Start the animation
        self.temp_animation.start()

    def load_templates(self):
        self.templates = {}

        try:
            # Get all YAML files in the template folder
            template_files = Path(TEMPLATES_FOLDER).rglob('*.yaml')

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

    def save_template(self):
        current_dir = os.getcwd()
        dir_path = os.path.join(current_dir, TEMPLATES_FOLDER)
        if os.path.isdir(dir_path):
            start_dir = dir_path
        else:
            start_dir = ''

        accepted_file_types = ['.yaml', '.yml']
        allowed_types = [f'*{fp}' for fp in accepted_file_types]
        self.accepted_filetypes = ';'.join(allowed_types)

        file_path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption='Save Template',
            directory=start_dir,
            filter=f'YAML Files ({self.accepted_filetypes})',
        )

        if not file_path:
            return

        template_dict = {}
        # Get all the data from the template editor
        for name, line_edit in self.template_fields.items():
            if isinstance(line_edit, PositiveIntegerInput):
                template_dict[name] = int(line_edit.text())
            else:
                template_dict[name] = line_edit.text()

        regions = []
        for region in self.template_regions:
            region_dict = {}
            for name, line_edit in region.items():
                if isinstance(line_edit, list):
                    region_dict[name] = [
                        int(coord.text()) for coord in line_edit]
                elif isinstance(line_edit, PositiveIntegerInput):
                    region_dict[name] = int(line_edit.text())
                else:
                    region_dict[name] = line_edit.text()
            regions.append(region_dict)

        template_dict['regions'] = regions

        with open(file_path, 'w') as file:
            yaml.dump(template_dict, file)

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
        QImage.Format.Format_BGR888
    )
