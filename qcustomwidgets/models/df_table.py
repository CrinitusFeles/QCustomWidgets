from copy import copy
from typing import Callable
import pandas as pd
from PyQt6 import QtWidgets, QtGui, QtCore


def calculate_color(val, row: int, column: str,
                    mask, default_color, ok_color, err_color):
    if column == 'ErrCnt':
        if val > 0:
            return QtGui.QBrush(err_color)
    if mask[row]:
        return QtGui.QBrush(default_color)  # QtCore.Qt.GlobalColor.white
    else:
        return QtGui.QBrush(err_color)


DISPLAY_ROLE= QtCore.Qt.ItemDataRole.DisplayRole


class DfModel(QtGui.QStandardItemModel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.header_labels: list[str] = []

    def headerData(self, section, orientation, role=DISPLAY_ROLE):
        if role == DISPLAY_ROLE and orientation == QtCore.Qt.Orientation.Horizontal and self.header_labels:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)


class DataFrameTable(QtWidgets.QTableView):
    def __init__(self, drop_columns: list[str] | None = None) -> None:
        super().__init__()
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalScrollMode(QtWidgets.QTableView.ScrollMode.ScrollPerPixel)
        self._model = DfModel()
        self.setStyleSheet("QTableView::item {padding-right: 30px;}")
        self.setModel(self._model)
        self.original_data: pd.DataFrame = pd.DataFrame()
        self.drop_columns: list[str] = drop_columns or []
        self.on_download: Callable | None = None
        self._mask: list[bool] | None = None
        self.keep_color_column: str = 'ErrCnt'
        self.keep_color_condition = lambda x: x > 0

    def set_data(self, df: pd.DataFrame, mask: list[bool] | None = None):
        self.original_data = df.copy(True)
        self._mask = copy(mask) if mask else None
        self._model.clear()
        self._model.header_labels = [str(key) for key in list(df)
                                     if key not in self.drop_columns]
        self._model.setColumnCount(len(self._model.header_labels))
        data: list[dict] = list(df.T.to_dict().values())
        err_color = ["#DD571C", "#7E0000"][self.isDark()]
        for i, row in enumerate(data):
            items = []
            for key, val in row.items():
                if key not in self.drop_columns:
                    item = QtGui.QStandardItem(f'{val}')
                    if mask and not mask[i]:
                        item.setBackground(QtGui.QColor(err_color))
                    if key == self.keep_color_column and self.keep_color_condition(val):
                        item.setBackground(QtGui.QColor(err_color))
                    items.append(item)
            self._model.appendRow(items)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    # def changeEvent(self, a0: QtCore.QEvent | None):
    #     super().changeEvent(a0)
    #     if a0:
    #         t = a0.type()
    #         if t == a0.Type.PaletteChange:
    #             if self.isDark():
    #                 ...

    def isDark(self) -> bool:
        base = self.palette().base().color().value()
        text = self.palette().text().color().value()
        return base < text


if __name__ == '__main__':

    df_raw = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                    'b': [100, 200, 300],
                    'IsErr': [True, False, True],
                    'c': ['a', 'b', 'c'],
                    'ErrCnt': [1, 0, 0],})
    # df = df_raw.drop('IsErr', axis=1)
    mask = df_raw['IsErr'].to_list()
    app = QtWidgets.QApplication([])
    view = DataFrameTable(['IsErr'])
    view.set_data(df_raw, mask)
    header = view.horizontalHeader()
    # header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
    # header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
    view.resize(800, 600)
    view.show()
    app.exec()