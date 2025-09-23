from pathlib import Path
from typing import Literal
from PyQt6 import QtCore, QtWidgets
from qcustomwidgets.widgets.image_box import ImageBox
from qcustomwidgets.widgets.button import Button
from qcustomwidgets.style.palettes import dark
from qcustomwidgets.style.stylesheets import stylesheet


class TabBar(QtWidgets.QTabBar):
    def paintEvent(self, a0) -> None:
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.ControlElement.CE_TabBarTabShape, opt)
            painter.save()

            s: QtCore.QSize = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c: QtCore.QPoint = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.ControlElement.CE_TabBarTabLabel, opt)
            painter.restore()


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self,
                 tab_bar_position: Literal['top', 'bottom',
                                           'left', 'right'] = 'top',
                 parent: QtWidgets.QWidget | None = None,) -> None:
        super().__init__(parent)
        self.tabs: list[tuple[Button, QtWidgets.QWidget]] = []
        if tab_bar_position in ['left', 'right']:
            self.tab_bar = TabBar(self)
            self.setTabBar(self.tab_bar)
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        else:
            self.tab_bar: QtWidgets.QTabBar = self.tabBar()  # type: ignore
        self.currentChanged.connect(self._on_current_changed)
        self._last_index: int = 0

    def _on_current_changed(self, val: int):
        if val < len(self.tabs):
            self.tabs[val][0].enterEvent(None)
            self.tabs[val][0]._is_active = True
            self.tabs[self._last_index][0]._is_active = False
            self.tabs[self._last_index][0].leaveEvent(None)
            self._last_index = val

    def addTab(self, widget: QtWidgets.QWidget, label: str,  # type: ignore
               icon: ImageBox | str | Path | None = None,
               tooltip: str | None =  None):
        super().addTab(widget, None)
        btn = Button(label,
                     [icon] if icon is not None else None,
                     flat=True,
                     tooltip=tooltip)
        btn.setFixedSize(40, 40)
        btn.setIconSize(30, 30)
        btn.setContentsMargins(5, 5, 5, 5)
        index: int = self.count() - 1
        btn.pressed.connect(lambda: self.setCurrentIndex(index))
        self.tabs.append((btn, widget))
        pos = QtWidgets.QTabBar.ButtonPosition.LeftSide
        self.tab_bar.setTabButton(index, pos, btn)



if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    dark()
    # QtWidgets.QApplication.setStyle(ProxyStyle())
    w = TabWidget('left')
    assets = Path(__file__).parents[1] / 'assets'
    w.addTab(QtWidgets.QWidget(), "", assets / 'register.svg')
    w.addTab(QtWidgets.QWidget(), "", assets / 'register.svg')
    w.addTab(QtWidgets.QWidget(), "", assets / 'register.svg')

    w.resize(640, 480)
    w.show()

    sys.exit(app.exec())