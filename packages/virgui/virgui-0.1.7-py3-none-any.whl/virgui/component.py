from __future__ import annotations

from finesse.element import ModelElement
from PySide6 import QtCore, QtWidgets


class ModelElementRectItem(QtWidgets.QGraphicsRectItem):

    def __init__(
        self, x: float, y: float, width: float, height: float, element: ModelElement
    ):
        self.element = element
        super().__init__(x, y, width, height)
        self.setPen(QtCore.Qt.NoPen)
