from pathlib import Path
from PyQt6 import QtWidgets
from PyQt6.QtGui import QMouseEvent
from PyQt6.uic.load_ui import loadUi
from qcustomwidgets import ImageBox, FlowLayout, icons, images


class IconWidget(QtWidgets.QWidget):
    def __init__(self, icon_path: Path|str) -> None:
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout(self)
        self.icon = ImageBox(icon_path)
        self.icon.setFixedHeight(50)
        self._layout.addWidget(self.icon)
        if isinstance(icon_path, str):
            name: str = icon_path
        else:
            name = icon_path.stem
        self.label = QtWidgets.QLineEdit(name)
        self.label.setReadOnly(True)
        self._layout.addWidget(self.label)

    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:
        super().mouseReleaseEvent(a0)
        clipboard = QtWidgets.QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.label.text())
            print('Copied')


class Gallery(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent / 'icon_gallery.ui', self)
        self.verticalLayout: QtWidgets.QVBoxLayout
        self.flow_layout = FlowLayout()
        self.verticalLayout.addLayout(self.flow_layout)
        for ext in ['svg', 'png']:
            file_path: Path = Path(__file__).parents[1] / 'assets' / ext
            for file in file_path.glob(f'*.{ext}'):
                btn = IconWidget(f':/{ext}/{file.stem}')
                self.flow_layout.addWidget(btn)



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = Gallery()
    w.show()
    app.exec()