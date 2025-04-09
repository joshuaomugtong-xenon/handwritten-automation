from PyQt6.QtWidgets import QLayout
import cv2

type MatLike = cv2.typing.MatLike


def clear_layout(layout: QLayout = None):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            child_layout = item.layout()
            if child_layout is not None:
                clear_layout(child_layout)
                child_layout.deleteLater()
