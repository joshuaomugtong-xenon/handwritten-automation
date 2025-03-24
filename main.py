import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import qdarktheme

from ui.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 12))
    qdarktheme.setup_theme()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
