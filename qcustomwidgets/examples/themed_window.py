
from PyQt6 import QtWidgets, QtCore
from qcustomwindow import CustomWindow, stylesheet
from qcustomwidgets import Button, __version__, dark, light


class ThemedWindow(CustomWindow):
    def __init__(self, version: str = '') -> None:
        super().__init__()
        self.theme_button = Button('', [':/svg/dark', ':/svg/light'],
                                   flat=True, iterate_icons=True)
        self.theme_button.clicked.connect(self.change_theme)
        self.add_right_widget(self.theme_button)

        self.pin_button = Button('', [':/svg/pin'], flat=True)
        self.pin_button.setCheckable(True)
        self.pin_button.clicked.connect(self.on_pin)
        self.add_right_widget(self.pin_button)
        # self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)

        if version:
            self.version_button = Button(version)
            self.add_left_widget(self.version_button)

        app = QtWidgets.QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
        self.is_dark: bool = False

    def on_pin(self):
        if self.pin_button.isChecked():
            self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | self.windowFlags())
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def change_theme(self):
        light() if self.is_dark else dark()
        self.is_dark = not self.is_dark


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ThemedWindow(__version__)
    w.show()
    app.exec()