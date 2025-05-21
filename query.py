import sys
import os
import json
import qdarktheme
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QListWidget, QTableWidget, QTableWidgetItem,
    QSplitter, QLabel, QHBoxLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 12))
    qdarktheme.setup_theme()
    window = QueryApp()
    window.show()
    sys.exit(app.exec())


class QueryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_title = 'Project Query'
        self.search_path = 'data'

        self.found_files = {}

        self.initUI()
        self.showMaximized()

    def initUI(self):
        self.setWindowTitle(self.app_title)
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_label = QLabel("Search:")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter search term...")
        self.search_bar.textChanged.connect(self.search_files)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        layout.addWidget(search_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.display_json)
        splitter.addWidget(self.results_list)

        self.json_table = QTableWidget()
        splitter.addWidget(self.json_table)

        splitter.setSizes([300, 900])
        layout.addWidget(splitter)

        layout.setStretchFactor(splitter, 1)

    def search_files(self):
        self.results_list.clear()
        self.json_table.clear()
        search_term = self.search_bar.text().lower()
        self.found_files = {}

        if not search_term:
            return

        for root, _, files in os.walk(self.search_path):
            for file in files:
                if not file.endswith('.json'):
                    continue
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        json_data = json.load(f)
                        found = self.search_json(json_data, search_term)
                        found |= search_term in file.lower()
                        if found:
                            self.found_files[file] = {
                                'path': file_path,
                                'data': json_data
                            }
                            self.results_list.addItem(file)
                except Exception as e:
                    print(f'Error reading file {file_path}, skipped: {e}')
                    continue

    def search_json(self, data, term):
        # Recursively search through JSON data for the search term
        # Flexible to handle nested dictionaries and lists
        if isinstance(data, dict):
            for key, value in data.items():
                if term in str(key).lower() or term in str(value).lower():
                    return True
                if isinstance(value, (dict, list)) and \
                        self.search_json(value, term):
                    return True
        elif isinstance(data, list):
            for item in data:
                if term in str(item).lower():
                    return True
                if isinstance(item, (dict, list)) and \
                        self.search_json(item, term):
                    return True
        return False

    def display_json(self, item):
        file_name = item.text()
        json_data = self.found_files[file_name]['data']

        table_data = self.flatten_json(json_data)

        self.json_table.setRowCount(len(table_data))
        self.json_table.setColumnCount(2)
        self.json_table.setHorizontalHeaderLabels(['Key', 'Value'])

        for i, (key, value) in enumerate(table_data.items()):
            key_item = QTableWidgetItem(str(key))
            value_item = QTableWidgetItem(str(value))

            key_item.setFlags(key_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.json_table.setItem(i, 0, key_item)
            self.json_table.setItem(i, 1, value_item)

        self.json_table.resizeColumnToContents(0)

        header = self.json_table.horizontalHeader()
        header.setStretchLastSection(True)

    def flatten_json(self, data, parent_key='', sep='.'):
        # Flatten JSON data into a dictionary
        items = {}
        pairs = data.items() if isinstance(data, dict) else enumerate(data)
        for key, value in pairs:
            new_key = f"{parent_key}{sep}{key}" if parent_key else str(key)

            if isinstance(value, (dict, list)):
                items.update(self.flatten_json(value, new_key, sep=sep))
            else:
                items[new_key] = value
        return items


if __name__ == '__main__':
    main()
