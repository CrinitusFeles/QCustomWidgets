from PyQt6 import QtWidgets
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QEnterEvent, QResizeEvent
from qcustomwidgets import Button, ImageBox


class SearchLineEdit(QtWidgets.QLineEdit):
    def __init__(self) -> None:
        super().__init__()
        self.clear_button = Button('', [':/svg/close'], self, True)
        self.clear_button.setVisible(False)
        self.clear_button.clicked.connect(self.clear)
        self.search_icon = ImageBox(':/svg/search', self)
        self.search_icon.setFixedSize(25, 25)
        self.setContentsMargins(25, 0, 0, 0)
        self.setPlaceholderText('Search')

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self.clear_button.move(self.width() - 25, 0)
        self.clear_button.setFixedHeight(self.height())
        self.search_icon.setFixedHeight(self.height())
        return super().resizeEvent(a0)

    def enterEvent(self, event: QEnterEvent | None) -> None:
        self.clear_button.setVisible(True)
        return super().enterEvent(event)

    def leaveEvent(self, a0: QEvent | None) -> None:
        self.clear_button.setVisible(False)
        return super().leaveEvent(a0)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = SearchLineEdit()
    w.show()
    app.exec()