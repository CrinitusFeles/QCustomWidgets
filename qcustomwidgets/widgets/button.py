from pathlib import Path
from typing import Iterable, Sequence
from typing_extensions import override
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QAbstractButton,
    QGraphicsDropShadowEffect,
    QApplication,
    QStackedLayout
)
from PyQt6.QtGui import QColor, QMouseEvent, QPainter, QPen, QBrush, QPalette
from qcustomwidgets.style.palettes import dark, light
from qcustomwidgets.widgets.image_box import ImageBox


ICON_SOURCE = Sequence[ImageBox | str | Path] | ImageBox | str | Path


class Button(QAbstractButton):
    def __init__(self, text="", icons: ICON_SOURCE | None = None,
                 parent=None, flat: bool = False,
                 iterate_icons: bool = False, tooltip: str | None = None,
                 constant_color: bool = False) -> None:
        super().__init__(parent)
        self.setMinimumSize(50, 25)
        self.setToolTip(tooltip)
        self._layout = QHBoxLayout()
        margin: int = 0 if flat else 15
        self._layout.setContentsMargins(margin, 0, margin, 0)
        self.setLayout(self._layout)

        self.body = QWidget()
        self.body_layot = QHBoxLayout()
        self.body_layot.setContentsMargins(0, 0, 0, 0)
        self.body.setLayout(self.body_layot)
        self._layout.addWidget(self.body,
                               alignment=Qt.AlignmentFlag.AlignCenter)
        self.icons_stack = QStackedLayout()
        # self.icons_stack.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_layot.addLayout(self.icons_stack)

        self._icon_constant_color: bool = constant_color
        self._text: str = text
        self.label = QLabel(text)
        if not self._text:
            self.label.setVisible(False)
            if flat:
                self.setFixedSize(25, 25)
        self.body_layot.addWidget(self.label,
                                  alignment=Qt.AlignmentFlag.AlignCenter)

        self._icons: list[ImageBox] = []
        if icons is not None:
            if isinstance(icons, Iterable):
                for _icon in icons:
                    self._add_icon(_icon)
            else:
                self._add_icon(icons)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0.8)
        self.shadow.setColor(QColor(0, 0, 0))
        self.shadow.setOffset(2, 2)

        if not flat:
            self.setGraphicsEffect(self.shadow)
        self.styleDict: dict = {
            "default": {
                "background-color": "transparent",
                "border-color": "transparent",
                "border-width": 1 if not flat else 0,
                "border-radius": 21,
                "font-family": None,
                "font-size": 12,
                "font-weight": "regular",
                "color":f"{self.palette_hex('text')}",
                "drop-shadow-radius": 20 if not flat else 0,
                "drop-shadow-offset": (0, 0),
                "drop-shadow-alpha": 100,
            },
            "hover": {
                "background-color": f"{self.palette_hex('base')}",
                "border-color": f"{self.palette_hex(('dark', 'button')[flat])}",
                "border-width": 1 if not flat else 0,
                "border-radius": 41 if not flat else 5,
                "font-size": 12,
                "font-weight": "regular",
                "color": f"{self.palette_hex('text')}",
                "drop-shadow-radius": 30 if not flat else 0,
                "drop-shadow-offset": (0, 0),
                "drop-shadow-alpha": 100,
            },
            "press": {
                "background-color": f"{self.palette_hex('base', darker=200)}",
                "border-color": f"{self.palette_hex(('dark', 'button')[flat])}",
                "border-width": 1 if not flat else 0,
                "border-radius": 11 if not flat else 5,
                "font-size": 12,
                "font-weight": "regular",
                "color": f"{self.palette_hex('text')}",
                "drop-shadow-radius": 0,
                "drop-shadow-offset": (0, 0),
                "drop-shadow-alpha": 100,
            },
        }

        self._hover = False
        self._press = False
        self._is_active = False
        self.is_flat: bool = flat
        if iterate_icons:
            self.clicked.connect(self.next_state)

    def _add_icon(self, icon_source: ImageBox | str | Path):
        if isinstance(icon_source, (str, Path)):
            icon: ImageBox = ImageBox(icon_source)
        else:
            icon = icon_source
        icon.setFixedSize(18, 18)
        self.icons_stack.addWidget(icon)
        self._icons.append(icon)
        icon.resizeEvent(None)

    def palette_hex(self, role: str, darker: int = 0, lighter: int = 0):
        color: QColor = getattr(self.palette(), role)().color()
        if darker > 0:
            new_color = color.darker(darker)
            return new_color.name()
        if lighter > 0:
            new_color = color.lighter(lighter)
            return new_color.name()
        return color.name()

    def icon_index(self):
        return self.icons_stack.currentIndex()

    @override
    def changeEvent(self, e: QEvent | None):
        super().changeEvent(e)
        if e:
            t = e.type()
            if t == e.Type.PaletteChange:
                self.styleDict["default"]["background-color"] = f"{(self.palette_hex('button'), 'transparent')[self.is_flat]}"
                self.styleDict["default"]["border-color"] = f"{(self.palette_hex('button'), 'transparent')[self.is_flat]}"
                self.styleDict["default"]["color"] = f"{self.palette_hex('text')}"
                self.styleDict["hover"]["background-color"] = f"{self.palette_hex(('base', 'button')[self.is_flat], darker=130)}"
                self.styleDict["hover"]["border-color"] = f"{self.palette_hex(('dark', 'button')[self.is_flat])}"
                self.styleDict["hover"]["color"] = f"{self.palette_hex('text')}"
                self.styleDict["press"]["background-color"] = f"{self.palette_hex(('base', 'button')[self.is_flat], darker=200)}"
                self.styleDict["press"]["border-color"] = f"{self.palette_hex(('dark', 'button')[self.is_flat])}"
                self.styleDict["press"]["color"] = f"{self.palette_hex('text')}"
                if self._icons and not self._icon_constant_color:
                    if self._is_active:
                        color: str = "#FFFFFF" if self.isDark() else '#000000'
                    else:
                        color = "#616161" if self.isDark() else "#898989"
                    for icon in self._icons:
                        icon.change_svg_color(color)
            elif t == e.Type.StyleChange:
                # print('style changed')
                ...

    def isDark(self) -> bool:
        base = self.palette().base().color().value()
        text = self.palette().text().color().value()
        return base < text

    def set_current_icon_color(self, color: str):
        if self._icons:
            icon: ImageBox = self._icons[self.icons_stack.currentIndex()]
            icon.change_svg_color(color)

    def change_icons_color(self, color: str):
        if self._icons:
            for icon in self._icons:
                icon.change_svg_color(color)

    def current_icon(self) -> ImageBox | None:
        if self._icons:
            i: int = self.icons_stack.currentIndex()
            return self._icons[i]

    def set_state(self, state: int) -> None:
        if self._icons and state < len(self._icons):
            self.icons_stack.setCurrentIndex(state)
            self._check_state()

    def next_state(self) -> None:
        if self._icons:
            new_state: int = self.icons_stack.currentIndex() + 1
            if new_state > len(self._icons) - 1:
                new_state = 0
            self.icons_stack.setCurrentIndex(new_state)
            self._check_state()

    def _check_state(self):
        state = self.current_state()
        if state == 'default':
            self.leaveEvent(None)
        elif state == 'hover':
            self.enterEvent(None)


    @override
    def setText(self, text: str | None) -> None:
        if not text:
            text = ""
        self._text = text
        self.label.setText(self._text)

    def text(self) -> str:
        return self._text

    @override
    def setIcon(self, icon: ImageBox, index: int = 0) -> None:  # type: ignore
        if self._icons:
            old_icon: ImageBox = self._icons.pop(index)
            self._icons.insert(index, icon)
            self.icons_stack.replaceWidget(old_icon, icon)
        icon.setFixedSize(18, 18)
        icon.resizeEvent(None)

    @override
    def setIconSize(self, width: int, height: int):  # type: ignore
        if self._icons:
            for icon in self._icons:
                icon.setFixedSize(width, height)

    @override
    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        self._press = True
        return super().mousePressEvent(e)

    @override
    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        self._press = False
        return super().mouseReleaseEvent(e)

    @override
    def enterEvent(self, event) -> None:
        self._hover = True
        icon = self.current_icon()
        if icon and not self._is_active and not self._icon_constant_color:
            color: str = "#FFFFFF" if self.isDark() else '#000000'
            icon.change_svg_color(color)
        super().enterEvent(event)

    @override
    def leaveEvent(self, a0) -> None:
        self._hover = False
        icon = self.current_icon()
        if icon and not self._is_active and not self._icon_constant_color:
            color: str = "#898989" if self.isDark() else '#616161'
            icon.change_svg_color(color)
        super().leaveEvent(a0)

    def current_state(self):
        if self._press:
            return 'press'
        elif self._hover:
            return 'hover'
        else:
            return 'default'

    def animate_border_color(self, painter: QPainter):
        pc = QColor(self.styleDict[self.current_state()]["border-color"])
        if self.is_flat:
            pw = 0
        else:
            pw = self.styleDict[self.current_state()]["border-width"]
        pen = QPen(pc, pw)
        painter.setPen(pen)
        return painter

    def animate_background(self, painter: QPainter):
        b = QColor(self.styleDict[self.current_state()]["background-color"])
        brush = QBrush(b)
        painter.setBrush(brush)
        return painter

    def animate_border_corners(self, painter: QPainter):
        r_: int = self.styleDict[self.current_state()]["border-radius"]
        if r_ > self.height() / 2:
            r: int = self.height() // 2
        else:
            r = int(r_)
        painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, r, r)

    def animate_label(self):
        fc = QColor(self.styleDict[self.current_state()]["color"])
        plt = self.label.palette()
        plt.setColor(self.label.foregroundRole(), fc)
        self.label.setPalette(plt)

        fs = self.styleDict[self.current_state()]["font-size"]
        fnt = self.label.font()
        fnt.setPixelSize(int(fs))
        if self.styleDict["default"]["font-family"]:
            fnt.setFamily(self.styleDict["default"]["font-family"])
        self.label.setFont(fnt)

    def paint_shadows(self):
        dsr = self.styleDict[self.current_state()]["drop-shadow-radius"]
        dso = self.styleDict[self.current_state()]["drop-shadow-offset"]
        dsc = self.styleDict[self.current_state()]["drop-shadow-alpha"]
        if dsr == 0:
            self.shadow.setEnabled(False)
        else:
            self.shadow.setEnabled(True)
            self.shadow.setBlurRadius(dsr)
            self.shadow.setOffset(*dso)
            self.shadow.setColor(QColor(0, 0, 0, dsc))

    @override
    def paintEvent(self, e):
        pt = QPainter()
        pt.begin(self)
        pt.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.is_flat:
            self.paint_shadows()
        self.animate_label()
        self.animate_border_color(pt)
        self.animate_background(pt)
        self.animate_border_corners(pt)
        pt.end()
        self.update()


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        assets = Path(__file__).parents[1] / 'assets'
        self._layout = QHBoxLayout()
        icons = [
            ImageBox(assets / 'dark.svg'),
            ImageBox(assets / 'light.svg')
        ]
        self.b = Button('hello', icons, flat=True, iterate_icons=True)
        self.b.clicked.connect(self.on_pressed)
        self._layout.addWidget(self.b)
        self.setLayout(self._layout)
        self.state = False

    def on_pressed(self):
        # colors = ["#230AB4", "#21A423", "#902424"]
        # self.b.change_icons_color(colors[random.randint(0, 2)])
        self.state = not self.state

        light() if self.state else dark()


if __name__ == '__main__':
    app = QApplication([])
    dark()
    w = Widget()
    w.show()
    app.exec()
