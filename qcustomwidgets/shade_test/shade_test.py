from pathlib import Path
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QImage, QPixmap
from PyQt6.uic.load_ui import loadUi


class Shade(QtWidgets.QLabel):
    prev_step_button: QtWidgets.QPushButton
    next_step_button: QtWidgets.QPushButton
    close_button: QtWidgets.QPushButton
    main_layout: QtWidgets.QVBoxLayout
    def __init__(self, parent: QtWidgets.QWidget,
                 target: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        ui_path: Path = Path(__file__).parent.joinpath('shade.ui')
        loadUi(ui_path, self)
        self.target: QtWidgets.QWidget | None = target
        self._parent: QtWidgets.QWidget = parent
        self.label = QtWidgets.QLabel('some description text some description text some description text some description text some description textsome description text', self)
        self.label.setWordWrap(True)
        self.label.adjustSize()
        self.label.setMargin(10)
        self.label.stackUnder(self.prev_step_button)
        self.label.stackUnder(self.next_step_button)
        self.label.stackUnder(self.close_button)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.pad = 1
        self.enable = False

    def on_close_button_clicked(self):
        self.enable = False
        self.setVisible(False)

    def update_target(self, target: QtWidgets.QWidget) -> None:
        self.target = target
        self._update()

    def _update(self) -> None:
        if not self.target:
            return
        img = QImage(self._parent.size(),
                     QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(QtGui.qRgba(0,0,0,120))
        p = QPainter(img)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        gp: QPoint = self.target.mapToGlobal(QPoint(0, 0))
        geom: QPoint = self.mapFromGlobal(gp)

        p.eraseRect(geom.x() - self.pad,
                    geom.y() - self.pad,
                    self.target.width() + self.pad * 2,
                    self.target.height() + self.pad * 2)
        self._draw_description(p)
        self.setPixmap(QPixmap.fromImage(img))
        del p
        del img

    def _calc_description_pos(self):
        if not self.target:
            return
        gp = self.target.mapToGlobal(QPoint(0, 0))
        geom = self.mapFromGlobal(gp)
        x: int = geom.x()
        y: int = geom.y()
        t_w: int = self.target.width()
        l_w: int = self.label.width()
        h: int = self.label.height()
        top_rect = QRect(x + t_w // 2 - l_w // 2,
                        y - h - 20,
                        t_w, h)
        right_rect = QRect(x + t_w + 20,
                          y - h // 2,
                          t_w, h)
        bottom_rect = QRect(x + t_w // 2 - l_w // 2,
                          y + h - 40,
                          t_w, h)
        left_rect = QRect(x - l_w - 20,
                          y - h // 2,
                          t_w, h)
        w = self.width()
        if bottom_rect.y() + self.label.height() < self.height():
            if bottom_rect.x() + l_w > w:
                return left_rect
            elif bottom_rect.x() < 0:
                return right_rect
            else:
                return bottom_rect
        if top_rect.y() > 0:
            if top_rect.x() + l_w > w:
                return left_rect
            elif top_rect.x() < 0:
                return right_rect
            else:
                return top_rect
        if right_rect.x() + l_w < w:
            return right_rect
        if left_rect.x() > 0:
            return left_rect

    def _draw_description(self, p: QPainter):
        g = self._calc_description_pos()
        if g is None:
            return
        self.label.setGeometry(g)
        self.label.adjustSize()
        geom: QRect = self.label.geometry()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        path = QtGui.QPainterPath()
        brush = QtGui.QBrush(Qt.GlobalColor.white)
        p.setBrush(brush)
        rect = QtCore.QRectF(geom.x() - self.pad,
                             geom.y() - self.pad,
                             geom.width() + self.pad * 2,
                             geom.height() + self.pad * 2
                             )
        path.addRoundedRect(rect, 10, 10)
        p.setClipPath(path)
        p.fillPath(path, p.brush())


    def resizeEvent(self, a0: QtGui.QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        if self.enable:
            self._update()


class MainWidget(QtWidgets.QWidget):

    help_button: QtWidgets.QPushButton
    p0: QtWidgets.QPushButton
    p1: QtWidgets.QPushButton
    p2: QtWidgets.QPushButton
    p3: QtWidgets.QPushButton
    p4: QtWidgets.QPushButton
    p5: QtWidgets.QPushButton
    p6: QtWidgets.QPushButton
    p7: QtWidgets.QPushButton
    p8: QtWidgets.QPushButton
    def __init__(self) -> None:
        super().__init__()
        ui_path: Path = Path(__file__).parent.joinpath('test.ui')
        loadUi(ui_path, self)
        self.shade = Shade(self, self.p0)
        self.shade.setVisible(False)
        self.shade.next_step_button.pressed.connect(self.on_next)
        self.shade.prev_step_button.pressed.connect(self.on_prev)

        self.help_button.pressed.connect(self.on_help)

        self.states = {
            0: self.p0,
            1: self.p1,
            2: self.p2,
            3: self.p3,
            4: self.p4,
            5: self.p5,
            6: self.p6,
            7: self.p7,
            8: self.p8,
        }
        self.index = 0

    def on_help(self):
        self.shade.enable = not self.shade.enable
        self.shade.setVisible(not self.shade.isVisible())

    def on_next(self):
        if self.index + 1 < len(self.states):
            self.index += 1
            self.shade.update_target(self.states[self.index])

    def on_prev(self):
        if self.index > 0:
            self.index -= 1
            self.shade.update_target(self.states[self.index])


    def resizeEvent(self, a0: QtGui.QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        if a0 is not None:
            self.shade.resize(a0.size())
        return None

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = MainWidget()
    # widget.setGeometry(100, 100, 500, 500)
    # l.addWidget(label)
    # l.addWidget(button)

    widget.show()
    app.exec()