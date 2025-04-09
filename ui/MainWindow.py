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
    QProgressDialog,
    QFrame,
)
from PyQt6.QtGui import (
    QPixmap,
    QImage,
)
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QRectF,
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
from .RegionImage import RegionImage
from .RegionBox import RegionBox
from .TemplateWidget import TemplateWidget, TemplateUI, RegionUI
from .Label import Label
from .BooleanComboBox import BooleanComboBox
from .TextInput import TextInput

from modules.template_validation import Region, convert_template_to_dict


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

        self.datafields: dict[str, BooleanComboBox | TextInput] = {}
        self.templates: dict[str, Template] = {}

        self.load_templates()
        self.current_image_path = ''
        self.selected_template = ''

        self.template_ui: TemplateUI = None

        self.data_animation = QPropertyAnimation()
        self.temp_animation = QPropertyAnimation()

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
        self.photo_viewer.viewer.region_created.connect(self.region_created)
        self.main_widget.addWidget(self.photo_viewer)

        self.right_tab_widget = QTabWidget()
        self.main_widget.addWidget(self.right_tab_widget)

        self.data_scroll_area = QScrollArea()
        self.data_scroll_area.setWidgetResizable(True)
        self.right_tab_widget.addTab(self.data_scroll_area, 'Data')

        self.data_widget = QWidget()
        self.data_widget_layout = QVBoxLayout()
        # self.data_widget_layout.setContentsMargins(20, 20, 20, 20)
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
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        image_path, selected = dialog.get_selected_files()
        try:
            self.load_templates()
            self.process_image(image_path, selected)
        except Exception:
            ErrorDialog()

    def reload_data(self):
        if self.current_image_path == '' or self.selected_template == '':
            return
        try:
            self.load_templates()
            self.process_image(self.current_image_path, self.selected_template)
        except Exception:
            ErrorDialog()

    def process_image(self, image_path, selected):
        self.reset_datafields()
        self.current_image_path = image_path
        self.selected_template = selected

        template = self.templates[selected]
        regions = template.regions

        # Create progress dialog
        progress = QProgressDialog("Processing image...", "Cancel", 0, len(regions) + 3, self)
        progress.setWindowTitle("Progress")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setFixedSize(400, 100)
        progress.setValue(0)
        progress.show()

        # Initialize template
        progress.setLabelText("Initializing template...")
        length = template.length
        width = template.width
        self.template_ui = self.template_editor.init_ui(template)
        progress.setValue(1)

        if progress.wasCanceled():
            return

        # Load the image and align it
        progress.setLabelText("Aligning image...")
        image = cv2.imread(image_path)
        image = self.homography_aligner.align(image, length, width)

        pixmap = QPixmap.fromImage(create_image(image))
        self.photo_viewer.viewer.set_photo(pixmap)
        progress.setValue(2)

        if progress.wasCanceled():
            return

        centers = {}
        if not template.use_coordinates:
            centers, corners = self.roi_extractor.get_marker_locations(image)
            for _, corner in corners.items():
                ((x1, y1), _, (x2, y2), _) = corner
                # TODO: Add the marker to the image
                # self.add_rect(x1, y1, x2, y2)

        # Load the text recognition model
        progress.setLabelText("Loading the text recognition model...")
        self.text_recognizer.word_recognizer.load_model()
        progress.setValue(3)

        if progress.wasCanceled():
            return

        # Process each region in the template
        for i, region in enumerate(regions):
            progress.setLabelText(f"Processing region: {i + 1}/{len(regions)}")
            coordinates = []
            if template.use_coordinates:
                coordinates = region.coordinates
            else:
                coordinates = markers_to_coordinates(region.markers, centers)

            # Draw the ROI and add it to the photo viewer
            x1, y1, x2, y2 = coordinates
            region_box = RegionBox(x1, y1, x2 - x1, y2 - y1)

            # Add the region to the template editor and link it to the ui elements
            self.create_region(region_box, region, template.use_coordinates, False)

            # Crop the ROI
            cropped_region = self.roi_extractor.crop_roi_coordinates(image, *coordinates)
            gray_region = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)

            # Define the data groupbox first so the rect_item can scroll to it
            groupbox = QFrame()
            groupbox.setFrameShape(QFrame.Shape.Box)
            groupbox.setFrameShadow(QFrame.Shadow.Plain)
            groupbox.setLineWidth(1)
            groupbox.setMidLineWidth(0)
            groupbox.setStyleSheet(
                "QFrame[selected=true] { background-color: rgba(135, 206, 250, 0); "
                "border: 2px solid #4682B4; border-radius: 5px; }"
            )

            region_box.signals.highlight_data_groupbox.connect(
                self.scroll_to_data_groupbox(groupbox))
            region_box.signals.unhighlight_data_groupbox.connect(
                self.unhighlight_groupbox(groupbox))

            groupbox_layout = QVBoxLayout()
            groupbox.setLayout(groupbox_layout)

            groupbox_layout.addWidget(Label("Name:"))
            name_input = TextInput(region.name)
            name_input.setReadOnly(True)
            groupbox_layout.addWidget(name_input)

            value_label = Label('Value:')
            groupbox_layout.addWidget(value_label)
            field_widget = None

            if region.type == RegionType.ENCIRCLEMENT:

                field_widget = BooleanComboBox()
                groupbox_layout.addWidget(field_widget)
                has_circle = self.encirclement_detector.detect(gray_region)
                field_widget.setCurrentIndex(0 if has_circle else 1)

            elif region.type == RegionType.CHECKBOX:

                field_widget = BooleanComboBox()
                groupbox_layout.addWidget(field_widget)
                is_checked = self.checkbox_detector.detect(gray_region)
                field_widget.setCurrentIndex(0 if is_checked else 1)

            elif region.type == RegionType.TEXT:

                field_widget = TextInput()
                groupbox_layout.addWidget(field_widget)
                text = self.text_recognizer.recognize_text(cropped_region)
                field_widget.setText(text)

            else:
                # This should not happen because the template is validated
                # Update progress bar
                progress.setValue(3 + i)

                if progress.wasCanceled():
                    return
                continue

            self.datafields[region.name] = field_widget

            groupbox_layout.addWidget(Label('Image:'))

            # Display the ROI under the label
            pixmap = QPixmap.fromImage(create_image(cropped_region))
            roi_image = RegionImage()
            roi_image.setPixmap(pixmap)
            # When the ROI image is clicked on the data tab, it will zoom
            # to the ROI on the photo viewer
            roi_image.clicked.connect(self.zoom_to_region(region_box))

            groupbox_layout.addWidget(roi_image)

            self.data_widget_layout.addWidget(groupbox)

            # Update progress bar
            progress.setValue(4 + i)

            if progress.wasCanceled():
                return

        # Close the progress dialog
        progress.close()

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
        self.clear_boxes()
        self.template_editor.reset_layout()
        self.template_ui = None

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

    def region_box_coordinates_changed(
            self,
            x1_ui: QLineEdit,
            y1_ui: QLineEdit,
            x2_ui: QLineEdit,
            y2_ui: QLineEdit,
            ):
        def callback(x1: int, y1: int, x2: int, y2: int):
            if x1_ui:
                x1_ui.setText(str(x1))
            if y1_ui:
                y1_ui.setText(str(y1))
            if x2_ui:
                x2_ui.setText(str(x2))
            if y2_ui:
                y2_ui.setText(str(y2))
        return callback

    def zoom_to_region(self, region_box: RegionBox):
        def callback():
            self.photo_viewer.viewer.zoom_to_rect(region_box.rect())
            self.photo_viewer.viewer.unselect_all()
            region_box.setSelected(True)
            self.photo_viewer.viewer._scene.update()
        return callback

    def scroll_to_data_groupbox(self, groupbox: QGroupBox):
        def callback():
            vertical_scroll_bar = self.data_scroll_area.verticalScrollBar()
            widget_pos = groupbox.mapTo(self.data_widget, groupbox.rect().topLeft())

            # Create animation for vertical scrollbar
            self.data_animation = QPropertyAnimation(vertical_scroll_bar, b'value')
            self.data_animation.setDuration(300)
            self.data_animation.setStartValue(vertical_scroll_bar.value())
            self.data_animation.setEndValue(widget_pos.y())
            self.data_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            # Set the groupbox to be selected
            groupbox.setProperty('selected', True)
            groupbox.style().unpolish(groupbox)
            groupbox.style().polish(groupbox)
            groupbox.update()

            # Start the animation group
            self.data_animation.start()

        return callback

    def scroll_to_template_groupbox(self, groupbox: QFrame):
        def callback():
            # First scroll to the widget
            vertical_scroll_bar = self.template_scroll_area.verticalScrollBar()
            widget_pos = groupbox.mapTo(self.template_editor, groupbox.rect().topLeft())

            # Create animation for vertical scrollbar
            self.temp_animation = QPropertyAnimation(vertical_scroll_bar, b'value')
            self.temp_animation.setDuration(300)
            self.temp_animation.setStartValue(vertical_scroll_bar.value())
            self.temp_animation.setEndValue(widget_pos.y())
            self.temp_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            # Set the groupbox to be selected
            groupbox.setProperty('selected', True)
            groupbox.style().unpolish(groupbox)
            groupbox.style().polish(groupbox)
            groupbox.update()

            # Start the animation
            self.temp_animation.start()

        return callback

    def unhighlight_groupbox(self, groupbox: QFrame):
        def callback():
            groupbox.setProperty('selected', False)
            groupbox.style().unpolish(groupbox)
            groupbox.style().polish(groupbox)
            groupbox.update()

        return callback

    def region_created(self, rect: QRectF):

        # Create the region box
        x, y, w, h = rect.getRect()
        region_box = RegionBox(x, y, w, h)

        # Create the region
        x1, y1, x2, y2 = rect.getCoords()
        region = Region(
            name='',
            type='text',
            coordinates=[int(x1), int(y1), int(x2), int(y2)],
            markers=[0, 0, 0, 0],
        )

        self.create_region(region_box, region)

    def create_region(self, region_box: RegionBox, region: Region, use_coords: bool = True, is_edited: bool = True):
        # Add the region to the photo viewer
        self.photo_viewer.viewer._scene.addItem(region_box)
        # Make it selected
        region_box.setSelected(is_edited)
        # Make it editable
        region_box.set_edit_mode(is_edited)

        # Create the template region
        region_ui, tp_groupbox, link = self.template_editor.add_region(region, use_coords)
        # Add the region ui elements to the template ui elements
        self.template_ui.regions.append(region_ui)

        x1_input, y1_input, x2_input, y2_input = region_ui.coordinates
        region_box.signals.coordinates_changed.connect(
            self.region_box_coordinates_changed(x1_input, y1_input, x2_input, y2_input))
        region_box.signals.highlight_template_groupbox.connect(
            self.scroll_to_template_groupbox(tp_groupbox))
        region_box.signals.unhighlight_template_groupbox.connect(
            self.unhighlight_groupbox(tp_groupbox))
        region_box.signals.request_delete_region.connect(
            self.delete_region(region_box, tp_groupbox, region_ui))

        if link:
            link.clicked.connect(self.zoom_to_region(region_box))

    def delete_region(self, region_box: RegionBox, template_groupbox: QFrame, region_ui: RegionUI):
        def callback():
            # Remove the region from the photo viewer
            self.photo_viewer.viewer._scene.removeItem(region_box)
            # Remove the region from the template editor
            self.template_editor.remove_region(template_groupbox)
            # Remove the region from the datafields
            self.template_ui.regions.remove(region_ui)
        return callback

    def load_templates(self):
        self.templates.clear()

        try:
            # Get all YAML files in the template folder
            template_files = Path(TEMPLATES_FOLDER).rglob('*.yaml')

            for template_file in template_files:
                try:
                    # Validate the template
                    template = validate_template_file(template_file)
                    # Get the filename
                    filename = os.path.basename(template_file)

                    # Add the template to the dictionary
                    name = f'{filename}  |  \"{template.form_type} - {template.form_title}\"'
                    self.templates[name] = template
                except Exception:
                    # Skip the file if it is not a valid template
                    continue
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

        template_dict = convert_template_to_dict(self.template_ui.value())

        with open(file_path, 'w') as file:
            yaml.dump(template_dict, file, sort_keys=False)

    def clear_boxes(self):
        for item in self.photo_viewer.viewer._scene.items():
            if isinstance(item, RegionBox):
                self.photo_viewer.viewer._scene.removeItem(item)


type Point = tuple[int, int]


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
