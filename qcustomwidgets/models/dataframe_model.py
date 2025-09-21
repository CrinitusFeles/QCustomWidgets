from typing import Callable
import pandas as pd
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import pyqtSlot as Slot


def calculate_color(val, row: int, column: str,
                    mask, default_color, ok_color, err_color):
    if column == 'ErrCnt':
        if val > 0:
            return QtGui.QBrush(err_color)
    if mask[row]:
        return QtGui.QBrush(default_color)  # QtCore.Qt.GlobalColor.white
    else:
        return QtGui.QBrush(err_color)


MODEL_INDEX = QtCore.QModelIndex | QtCore.QPersistentModelIndex


class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole: int = QtCore.Qt.ItemDataRole.UserRole + 1000
    ValueRole: int = QtCore.Qt.ItemDataRole.UserRole + 1001

    def __init__(self, df=pd.DataFrame(),
                 mask: list[bool] | None = None) -> None:
        super().__init__()
        self._df: pd.DataFrame = df
        self.values_mask: list[bool] | None = mask
        self.palette = 'light'
        self.calculate_color: Callable = calculate_color
        self.ok_color: dict = {'dark': QtGui.QColor("#188b0f"),
                               'light': QtGui.QColor("#76ff5a")}
        self.err_color: dict = {'dark': QtCore.Qt.GlobalColor.darkRed,
                                'light': QtGui.QColor("#DD571C")}
        self.default_color: dict = {'dark': QtCore.Qt.GlobalColor.black,
                                    'light': QtCore.Qt.GlobalColor.white}

    def update_column(self, column: int) -> None:
        self.dataChanged.emit(self.index(0, column),
                              self.index(self.rowCount() - 1, column))

    def setDataFrame(self, dataframe: pd.DataFrame,
                     mask) -> None:
        self.beginResetModel()
        self._df = dataframe.copy()
        if mask is not None:
            self.values_mask = mask.copy()
        self.endResetModel()

    Slot(int, QtCore.Qt.Orientation)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: int = QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._df.columns[section]
            else:
                header: str = ''
                try:
                    header = str(self._df.index[section])
                except IndexError as err:
                    print(f'{err}\n{self._df}\n{section=}')
                    raise err
                return header
        return None

    def rowCount(self, parent: MODEL_INDEX = QtCore.QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._df.index)

    def columnCount(self, parent: MODEL_INDEX = QtCore.QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return self._df.columns.size

    def data(self, index, role: int = QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()
                                       and 0 <= index.column() < self.columnCount()):
            return None
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        dt = self._df[col].dtype

        val = self._df.iloc[row][col]
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if isinstance(val, float):
                return str(f'{val:.2f}')
            else:
                return str(val)
        elif role == QtCore.Qt.ItemDataRole.BackgroundRole and self.values_mask is not None:
            r = index.row()
            color: QtGui.QBrush = self.calculate_color(val, r, col,
                                                       self.values_mask,
                                                       self.default_color[self.palette],
                                                       self.ok_color[self.palette],
                                                       self.err_color[self.palette])
            return color
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return None

    def roleNames(self):  # type: ignore
        roles = {
            QtCore.Qt.ItemDataRole.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


if __name__ == '__main__':

    df_raw = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                    'b': [100, 200, 300],
                    'IsErr': [True, False, True],
                    'c': ['a', 'b', 'c']})
    df = df_raw.drop('IsErr', axis=1)
    mask = df_raw['IsErr'].to_list()
    model = DataFrameModel(df, mask)
    app = QtWidgets.QApplication([])
    view = QtWidgets.QTableView()
    view.setModel(model)
    header = view.horizontalHeader()
    # header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
    # header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
    view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)  # type: ignore
    view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)  # type: ignore
    view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)  # type: ignore
    # view.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
    view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
    view.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    view.resize(800, 600)
    view.show()
    app.exec()