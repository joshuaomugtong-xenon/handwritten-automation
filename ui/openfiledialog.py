from __future__ import annotations
import os

from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
)
from PyQt6.QtCore import (
    Qt,
)

from modules.config import ACCEPTED_FILE_TYPES, SCANNED_FOLDER


class OpenFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Open File')
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        # self.setFixedSize(500, 100)

        allowed_types = [f'*{fp}' for fp in ACCEPTED_FILE_TYPES]
        self.accepted_filetypes = ';'.join(allowed_types)

        layout = QGridLayout()

        path_label = QLabel('Image File:')
        layout.addWidget(path_label, 0, 0)

        self.path_lineedit = QLineEdit()
        self.path_lineedit.setReadOnly(True)
        layout.addWidget(self.path_lineedit, 0, 1)

        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_image)
        layout.addWidget(browse_button, 0, 2)

        template_label = QLabel('Template:')
        layout.addWidget(template_label, 1, 0)

        self.template_combo = QComboBox()
        self.template_combo.addItems(self.parent().templates.keys())
        layout.addWidget(self.template_combo, 1, 1)

        reload_button = QPushButton('Reload')
        reload_button.clicked.connect(self.reload_templates)
        layout.addWidget(reload_button, 1, 2)

        button_layout = QHBoxLayout()

        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout, 2, 0, 1, 3)

        self.setLayout(layout)

    def browse_image(self):
        current_dir = os.getcwd()
        dir_path = os.path.join(current_dir, SCANNED_FOLDER)
        if os.path.isdir(dir_path):
            start_dir = dir_path
        else:
            start_dir = ''

        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open Image File',
            directory=start_dir,
            filter=f'Image Files ({self.accepted_filetypes})',
        )
        if file_path:
            self.path_lineedit.setText(file_path)

    def reload_templates(self):
        self.template_combo.clear()
        self.parent().load_templates()
        self.template_combo.addItems(self.parent().templates.keys())

    def get_selected_files(self):
        return self.path_lineedit.text(), self.template_combo.currentText()
