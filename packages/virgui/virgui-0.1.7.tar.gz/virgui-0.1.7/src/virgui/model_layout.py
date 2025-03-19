from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from finesse.components.general import ModelElement
from finesse.detectors import PowerDetector
from PySide6 import QtCore, QtGui, QtWidgets

from virgui.component import ModelElementRectItem
from virgui.parameter_table import ParameterTableModel
from virgui.parse_layout import LAYOUTS, parse_layout

if TYPE_CHECKING:
    pass

import virgui


class ZoomableGraphicsScene(QtWidgets.QGraphicsScene):

    def wheelEvent(self, event: QtWidgets.QGraphicsSceneWheelEvent) -> None:
        scale_factor = 1.15
        if event.delta() > 0:
            self.views()[0].scale(scale_factor, scale_factor)
        else:
            self.views()[0].scale(1 / scale_factor, 1 / scale_factor)
        event.accept()
        return super().wheelEvent(event)


class ModelLayout(QtWidgets.QWidget):

    def __init__(
        self,
        katscript_listener: Callable,
        katlog_listener: Callable,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent=parent)
        # it would be cleaner to define these in their respective classes
        # maybe there is something like an event listener
        self.katscript_listener = katscript_listener
        self.katlog_listener = katlog_listener

        self.setLayout(QtWidgets.QHBoxLayout())
        self.scene = ZoomableGraphicsScene(
            0, 0, 800, 800, backgroundBrush=QtGui.QBrush(QtCore.Qt.white)
        )
        self.scene.selectionChanged.connect(self.on_selection)
        self.switch_layout("cavity")
        # TODO user should define detectors or the layout should?
        self.circ = virgui.GLOBAL_MODEL.add(
            PowerDetector("circ", virgui.GLOBAL_MODEL.m2.p1.o)
        )
        self.trans = virgui.GLOBAL_MODEL.add(
            PowerDetector("trans", virgui.GLOBAL_MODEL.m2.p2.o)
        )
        self.refl = virgui.GLOBAL_MODEL.add(
            PowerDetector("refl", virgui.GLOBAL_MODEL.m1.p1.o)
        )

        # info window
        self.info_vbox = QtWidgets.QVBoxLayout()
        self.table_title = QtWidgets.QLabel(
            textFormat=QtCore.Qt.TextFormat.MarkdownText,
            textInteractionFlags=QtCore.Qt.TextInteractionFlag.TextBrowserInteraction,
            openExternalLinks=True,
        )
        self.table_view = QtWidgets.QTableView()
        self.info_vbox.addWidget(self.table_title)
        self.info_vbox.addWidget(self.table_view)

        self.view = QtWidgets.QGraphicsView(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)

        self.layout().addWidget(self.view)
        self.layout().addLayout(self.info_vbox)

    def switch_layout(self, layout_name: str):
        self.scene.clear()
        model, hitbox_mapping, svg_b_string = parse_layout(LAYOUTS / layout_name)
        virgui.GLOBAL_MODEL = model
        background_pixmap = QtGui.QPixmap()
        background_pixmap.loadFromData(svg_b_string)
        background = QtWidgets.QGraphicsPixmapItem(background_pixmap)
        self.scene.addItem(background)

        # add completely transparent rectangles as hitboxes, so users can select elements
        for comp_name, rect in hitbox_mapping.items():
            hitbox = ModelElementRectItem(
                rect.x, rect.y, rect.width, rect.height, model.get(comp_name)
            )
            self.scene.addItem(hitbox)

        for item in self.scene.items():
            if item is not background:
                item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        self.katscript_listener()
        # TODO maybe adjust the view here so everything is in focus?

    @QtCore.Slot()
    def on_selection(self):
        items = self.scene.selectedItems()
        if len(items) == 0:
            self.table_view.hide()
            self.table_title.setText("")
        elif len(items) == 1:
            item = items[0]
            assert isinstance(item, ModelElementRectItem)
            assert isinstance(item.element, ModelElement)
            el: ModelElement = item.element
            # maybe pre-create these instead of on the fly
            par_table = el.parameter_table(return_str=False)
            info_table = ParameterTableModel(par_table, el)
            info_table.dataChanged.connect(self.katscript_listener)
            info_table.parameter_changed.connect(self.katlog_listener)
            self.table_view.setModel(info_table)
            self.table_view.resizeRowsToContents()
            self.table_view.show()
            modules = el.__class__.__module__.split(".")
            doc_url = f"https://finesse.ifosim.org/docs/latest/api/{modules[1]}/{modules[2]}/{el.__class__.__module__}.{el.__class__.__name__}.html#{el.__class__.__module__}.{el.__class__.__name__}"
            self.table_title.setText(
                f"# [{el.__class__.__name__}]({doc_url}): {el.name}"
            )
        else:
            raise
