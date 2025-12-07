import time
from math import sin, radians
from typing_extensions import override

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QPen, QColor


class Spinner(QWidget):
    def __init__(self, line_width: int, color: str, size: int = 25) -> None:
        super().__init__()
        self.w: int = line_width
        self.color = QColor(color)
        self.angle: int = 0
        self.speed = 6
        self.play = True
        self.last_call: float = time.time()
        self.setFixedSize(size, size)

    @override
    def paintEvent(self, a0) -> None:
        pt = QPainter()
        pt.begin(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        w: int = self.w
        pen = QPen(self.color, w)
        pt.setPen(pen)
        s = min(self.width(), self.height())
        alen: float = ((sin(radians(self.angle / 16)) + 1) / 2) * (180 * 16)
        alen += ((sin(radians((self.angle / 16) + 130)) + 1) / 2) * (180 * 16)
        pt.drawArc(w, w, s - w * 2, s - w * 2,
                   self.angle, int(alen))
        pt.end()

        ep: float = (time.time() - self.last_call) * 1000
        self.last_call = time.time()

        self.angle += int(self.speed * ep)
        if self.angle > 360 * 16:
            self.angle = 0

        elif self.angle < 0:
            self.angle = 360 * 16

        if self.play:
            self.update()

if __name__ == '__main__':
    app = QApplication([])
    w = Spinner(4, 'green', 25)
    w.show()
    app.exec()