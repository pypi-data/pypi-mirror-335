import copy
import traceback
from typing import Any

from finesse.components.general import ModelElement
from finesse.parameter import Parameter
from finesse.utilities.tables import Table
from PySide6 import QtCore
from PySide6.QtCore import Qt


# https://www.pythonguis.com/tutorials/pyside6-qtableview-modelviews-nWumpy-pandas/
class ParameterTableModel(QtCore.QAbstractTableModel):
    parameter_changed = QtCore.Signal(Parameter, float, float)

    def __init__(self, finesse_table: Table, element: ModelElement):
        super().__init__()
        self._finesse_table = finesse_table
        self._element = element

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._finesse_table.table[1:, :][index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._finesse_table.table.shape[0] - 1

    def columnCount(self, index):
        return self._finesse_table.table.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._finesse_table.table[0, section])

    def flags(self, index: QtCore.QModelIndex):
        # only allow the values to be edited, not the labels
        if index.column == 0:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        else:
            return (
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsEditable
            )

    def setData(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        value: Any,
        /,
        role: int,
    ) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return super().setData(index, value, role)

        # Finesse table is in reversed order to match parameter decorator order
        p = list(reversed(self._element.parameters))[index.row()]
        # we need to create a copy
        old_val = float(copy.deepcopy(p.value))
        try:
            p.value = value
        except ValueError:
            print(f"Could not set {p} with value {value}")
            traceback.print_exc()
            return False

        self._finesse_table = self._element.parameter_table(return_str=False)
        self.dataChanged.emit(index, index, role)
        self.parameter_changed.emit(p, old_val, float(p.value))
        return True
