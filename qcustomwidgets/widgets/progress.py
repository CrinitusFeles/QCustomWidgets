from PyQt6 import QtWidgets


class Progress(QtWidgets.QProgressBar):
    def __init__(self) -> None:
        super().__init__()
        self.setTextVisible(False)
        self.placeholder = QtWidgets.QLabel()
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.placeholder)
        self.setMinimumHeight(35)

    def set_placeholder(self, text: str) -> None:
        self.placeholder.setText(text)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = Progress()
    w.setValue(50)
    w.set_placeholder('Text')
    w.show()
    app.exec()