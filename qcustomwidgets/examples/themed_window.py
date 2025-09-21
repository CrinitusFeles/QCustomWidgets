
from PyQt6 import QtWidgets
from qcustomwindow import CustomWindow, stylesheet
from qcustomwidgets import Button, __version__, dark, light


class ThemedWindow(CustomWindow):
    def __init__(self, version: str = '') -> None:
        super().__init__()
        self.theme_button = Button('', [':/svg/dark', ':/svg/light'],
                                   flat=True, iterate_icons=True)
        self.theme_button.clicked.connect(self.change_theme)
        if version:
            self.version_button = Button(version)
            self.add_left_widget(self.version_button)
        self.add_right_widget(self.theme_button)

        app = QtWidgets.QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
        self.is_dark: bool = False

    def change_theme(self):
        light() if self.is_dark else dark()
        self.is_dark = not self.is_dark


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ThemedWindow(__version__)
    w.show()
    app.exec()