from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QGroupBox,
    QFormLayout,
)

from modules.template_validation import Template, Region

from .Button import Button
from .Label import Label
from .TypeInput import TypeInput
from .TextInput import TextInput
from .PositiveIntegerInput import PositiveIntegerInput
from .BooleanInput import BooleanInput
from .Frame import Frame


class TemplateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self.region_layout = None

    def init_ui(self, template: Template):
        self.reset_layout()

        groupbox = QGroupBox('')
        self._layout.addWidget(groupbox)
        groupbox_layout = QFormLayout()
        groupbox.setLayout(groupbox_layout)

        form_type_ui = TextInput(template.form_type)
        groupbox_layout.addRow(Label('Form Type'), form_type_ui)

        form_title_ui = TextInput(template.form_title)
        groupbox_layout.addRow(Label('Form Title'), form_title_ui)

        length_ui = PositiveIntegerInput(str(template.length))
        groupbox_layout.addRow(Label('Length'), length_ui)

        width_ui = PositiveIntegerInput(str(template.width))
        groupbox_layout.addRow(Label('Width'), width_ui)

        use_coordinates_ui = BooleanInput(str(template.use_coordinates))
        groupbox_layout.addRow(Label('Use Coordinates'), use_coordinates_ui)

        regions_ui = []

        groupbox = QGroupBox('Regions')
        self._layout.addWidget(groupbox)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)
        self.region_layout = groupbox_layout

        return TemplateUI(
            form_type=form_type_ui,
            form_title=form_title_ui,
            length=length_ui,
            width=width_ui,
            use_coordinates=use_coordinates_ui,
            regions=regions_ui,
            )

    def add_region(
            self,
            region: Region,
            use_coords: bool = True,
            ):

        region_ui = RegionUI()

        groupbox = Frame()
        self.region_layout.addWidget(groupbox)
        groupbox_layout = QFormLayout()
        groupbox.setLayout(groupbox_layout)

        name_ui = TextInput(region.name)
        groupbox_layout.addRow(Label('Name'), name_ui)
        region_ui.name = name_ui

        type_ui = TypeInput(region.type)
        groupbox_layout.addRow(Label('Type'), type_ui)
        region_ui.type = type_ui

        link = None
        if use_coords:
            layout = QHBoxLayout()
            groupbox_layout.addRow(Label('Coordinates'), layout)

            for i, coord in enumerate(region.coordinates):
                coord_ui = PositiveIntegerInput(str(coord), 120)
                layout.addWidget(coord_ui)
                region_ui.coordinates[i] = coord_ui

            link = Button('Click to view')
            layout.addWidget(link)
        else:
            layout = QHBoxLayout()
            groupbox_layout.addRow(Label('Markers'), layout)

            for i, marker in enumerate(region.markers):
                marker_ui = PositiveIntegerInput(str(marker), 120)
                layout.addWidget(marker_ui)
                region_ui.markers[i] = marker_ui

        return region_ui, groupbox, link

    def remove_region(self, groupbox: Frame):
        self.region_layout.removeWidget(groupbox)
        groupbox.hide()
        groupbox.deleteLater()

    def reset_layout(self):
        self.clear_layout(self._layout)

    def clear_layout(self, layout: QLayout = None):
        if layout is None:
            layout = self.layout()
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


def title(string: str) -> str:
    return ' '.join([word.capitalize() for word in string.split('_')])


class RegionUI:

    def __init__(
            self,
            name: TextInput = None,
            type: TypeInput = None,
            coordinates: list[PositiveIntegerInput] = None,
            markers: list[PositiveIntegerInput] = None,
            ):

        self.name = name
        self.type = type
        self.coordinates = coordinates if coordinates else [None] * 4
        self.markers = markers if markers else [None] * 4

    def value(self) -> Region:

        return Region(
            name=self.name.value(),
            type=self.type.value(),
            coordinates=[coord.value() if coord else 0 for coord in self.coordinates],
            markers=[marker.value() if marker else 0 for marker in self.markers],
            )


class TemplateUI:

    def __init__(
            self,
            form_type: TextInput = None,
            form_title: TextInput = None,
            length: PositiveIntegerInput = None,
            width: PositiveIntegerInput = None,
            use_coordinates: BooleanInput = None,
            regions: list[RegionUI] = [],
            ):

        self.name = form_type
        self.description = form_title
        self.length = length
        self.width = width
        self.use_coordinates = use_coordinates
        self.regions = regions

    def value(self) -> Template:

        return Template(
            form_type=self.name.value(),
            form_title=self.description.value(),
            length=self.length.value(),
            width=self.width.value(),
            use_coordinates=self.use_coordinates.value(),
            regions=[region.value() for region in self.regions],
            )
