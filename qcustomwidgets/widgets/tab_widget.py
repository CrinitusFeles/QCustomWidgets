from pathlib import Path
from uuid import uuid4
from typing import Literal
from PyQt6 import QtCore, QtGui, QtWidgets
from qcustomwidgets.widgets.image_box import ImageBox
from qcustomwidgets.widgets.button import Button
from qcustomwidgets.style.palettes import dark
from qcustomwidgets.style.stylesheets import stylesheet
from qcustomwindow import CustomWindow


TAB_BTN_POS = QtWidgets.QTabBar.ButtonPosition.LeftSide


class TabBar(QtWidgets.QTabBar):
    onDetachTabSignal = QtCore.pyqtSignal(int, QtCore.QPoint)
    onMoveTabSignal = QtCore.pyqtSignal(int, int)
    detachedTabDropSignal = QtCore.pyqtSignal(str, int, QtCore.QPoint)

    def __init__(self, parent=None,
                 position: Literal['left', 'right', 'top', 'bottom'] = 'top'):
        QtWidgets.QTabBar.__init__(self, parent)

        self.setAcceptDrops(True)
        self.setElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.setSelectionBehaviorOnRemove(QtWidgets.QTabBar.SelectionBehavior.SelectLeftTab)

        self.dragStartPos = QtCore.QPoint()
        self.dragDropedPos = QtCore.QPoint()
        self.mouseCursor = QtGui.QCursor()
        self.dragInitiated = False
        self.position: Literal['left', 'right', 'top', 'bottom'] = position

    def get_tab_buttons_list(self) -> list[Button | None]:
        return [self.tabButton(i, TAB_BTN_POS) for i in range(self.count())]  # type: ignore

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent | None):
        if not a0:
            return
        a0.accept()
        self.onDetachTabSignal.emit(self.tabAt(a0.pos()), self.mouseCursor.pos())

    def mousePressEvent(self, a0: QtGui.QMouseEvent | None):
        if not a0:
            return
        if a0.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragStartPos = a0.pos()
        self.dragDropedPos.setX(0)
        self.dragDropedPos.setY(0)

        self.dragInitiated = False

        QtWidgets.QTabBar.mousePressEvent(self, a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent | None):
        if not a0:
            return

        # Determine if the current movement is detected as a drag
        if not self.dragStartPos.isNull():
            distance = (a0.pos() - self.dragStartPos).manhattanLength()
            if distance < QtWidgets.QApplication.startDragDistance():
                self.dragInitiated = True

        # If the current movement is a drag initiated by the left button
        if ((a0.buttons() & QtCore.Qt.MouseButton.LeftButton)) and self.dragInitiated:

            # Stop the move event
            finishMoveEvent = QtGui.QMouseEvent(QtCore.QEvent.Type.MouseMove,
                                                a0.pos().toPointF(),
                                                QtCore.Qt.MouseButton.NoButton,
                                                QtCore.Qt.MouseButton.NoButton,
                                                QtCore.Qt.KeyboardModifier.NoModifier)
            QtWidgets.QTabBar.mouseMoveEvent(self, finishMoveEvent)

            # Convert the move event into a drag
            drag = QtGui.QDrag(self)
            mimeData = QtCore.QMimeData()
            mimeData.setData('action', b'application/tab-detach')
            drag.setMimeData(mimeData)

            # Create the appearance of dragging the tab content
            parent_widget: QtWidgets.QTabWidget = self.parentWidget()  # type: ignore
            if not parent_widget:
                return
            pixmap = parent_widget.currentWidget().grab()  # type: ignore
            targetPixmap = QtGui.QPixmap(pixmap.size())
            targetPixmap.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(targetPixmap)
            painter.setOpacity(0.85)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            drag.setPixmap(targetPixmap)

            # Initiate the drag
            dropAction = drag.exec(QtCore.Qt.DropAction.MoveAction,
                                   QtCore.Qt.DropAction.IgnoreAction)

            # For Linux:  Here, drag.exec_() will not return MoveAction on Linux.  So it
            #             must be set manually
            if self.dragDropedPos.x() != 0 and self.dragDropedPos.y() != 0:
                dropAction = QtCore.Qt.DropAction.MoveAction

            # If the drag completed outside of the tab bar, detach the tab and move
            # the content to the current cursor position
            if dropAction in [QtCore.Qt.DropAction.IgnoreAction,
                              QtCore.Qt.DropAction.CopyAction]:
                a0.accept()
                # if dropAction == QtCore.Qt.DropAction.CopyAction:
                #     dropAction = self.action
                tab_index = self.tabAt(self.dragStartPos)
                self.onDetachTabSignal.emit(tab_index, self.mouseCursor.pos())

            # Else if the drag completed inside the tab bar, move the selected tab to the new position
            elif dropAction == QtCore.Qt.DropAction.MoveAction:
                if not self.dragDropedPos.isNull():
                    a0.accept()
                    self.onMoveTabSignal.emit(self.tabAt(self.dragStartPos),
                                              self.tabAt(self.dragDropedPos))
        else:
            QtWidgets.QTabBar.mouseMoveEvent(self, a0)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent | None):
        if not a0:
            return
        mimeData = a0.mimeData()
        if mimeData:
            formats = mimeData.formats()

            if 'action' in formats and mimeData.data('action') == 'application/tab-detach':
                a0.acceptProposedAction()

        QtWidgets.QTabBar.dragMoveEvent(self, a0)

    def dropEvent(self, a0: QtGui.QDropEvent | None):
        if not a0:
            return
        self.dragDropedPos = a0.position().toPoint()
        QtWidgets.QTabBar.dropEvent(self, a0)

    def detachedTabDrop(self, name, dropPos):
        tabDropPos = self.mapFromGlobal(dropPos)
        index = self.tabAt(tabDropPos)
        self.detachedTabDropSignal.emit(name, index, dropPos)

    def paintEvent(self, a0) -> None:
        if self.position in ['left', 'right']:
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
        else:
            super().paintEvent(a0)


class DetachedTab(CustomWindow):
    onCloseSignal = QtCore.pyqtSignal(QtWidgets.QWidget, str, str, Button)
    onDropSignal = QtCore.pyqtSignal(str, QtCore.QPoint)

    def __init__(self, tab_name: str, contentWidget: QtWidgets.QWidget,
                 icon: Button | None = None):
        super().__init__()
        self.button = icon
        self.tab_name: str = tab_name
        self.title_label: str  = tab_name
        if not tab_name:
            if self.button:
                self.button._press = False
                self.title_label = self.button.text() or self.button.toolTip()
                self.setTitle(self.title_label)
        else:
            self.setTitle(tab_name)
        self.contentWidget = contentWidget
        self.addWidget(self.contentWidget)
        if self.button:
            self.add_left_widget(self.button)
            self.button.setIconSize(25, 25)
            self.button.show()
        self.contentWidget.show()

        self.windowDropFilter = self.WindowDropFilter()
        self.titlebar.installEventFilter(self.windowDropFilter)
        self.windowDropFilter.onDropSignal.connect(self.windowDropSlot)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def windowDropSlot(self, dropPos):
        self.onDropSignal.emit(self.objectName(), dropPos)

    def closeEvent(self, a0):
        self.onCloseSignal.emit(self.contentWidget, self.objectName(),
                                self.title_label, self.button)

    ##
    #  An event filter class to detect a QMainWindow drop event
    class WindowDropFilter(QtCore.QObject):
        onDropSignal = QtCore.pyqtSignal(QtCore.QPoint)

        def __init__(self):
            QtCore.QObject.__init__(self)
            self.lastEvent = None
        ##
        #  Detect a QMainWindow drop event by looking for a NonClientAreaMouseMove (173)
        #  event that immediately follows a Move event
        #
        #  @param    obj    the object that generated the event
        #  @param    event  the current event
        def eventFilter(self, a0, a1):

            if not a1:
                return False
            # If a NonClientAreaMouseMove (173) event immediately follows a Move event...
            if a1.type() == QtCore.QEvent.Type.MouseButtonRelease:

                # Determine the position of the mouse cursor and emit it with the
                # onDropSignal
                mouseCursor = QtGui.QCursor()
                dropPos = mouseCursor.pos()
                self.onDropSignal.emit(dropPos)
                self.lastEvent = a1.type()
                return True

            else:
                self.lastEvent = a1.type()
                return False


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self,
                 tab_bar_position: Literal['top', 'bottom',
                                           'left', 'right'] = 'top',
                 parent: QtWidgets.QWidget | None = None,) -> None:
        super().__init__(parent)
        self.tab_bar = TabBar(self)
        self.tab_bar.onDetachTabSignal.connect(self.detachTab)
        self.tab_bar.onMoveTabSignal.connect(self.moveTab)
        self.tab_bar.detachedTabDropSignal.connect(self.detachedTabDrop)
        self.setTabBar(self.tab_bar)
        if tab_bar_position in ['left', 'right']:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self.currentChanged.connect(self.set_active_tab)

        self.detachedTabs = {}
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Shift+K'), self,
                                           self.closeDetachedTabs,
                                           context=QtCore.Qt.ShortcutContext.ApplicationShortcut)

        # Close all detached tabs if the application is closed explicitly
        QtWidgets.QApplication.instance().aboutToQuit.connect(self.closeDetachedTabs)  # type: ignore

    def setMovable(self, movable):
        pass

    def set_active_tab(self, val: int):
        buttons = self.tab_bar.get_tab_buttons_list()
        for i, btn in enumerate(buttons):
            if btn:
                btn.enterEvent(None)
                btn._is_active = (val == i)
                if val == i:
                    btn.enterEvent(None)
                btn.leaveEvent(None)

    def addTabCustom(self, widget: QtWidgets.QWidget | None, label: str,
                     icon: Button | ImageBox | str | Path | None = None,
                     tooltip: str | None = None,
                     insert_at: int | None = None,):
        if insert_at is None:
            index  = super().addTab(widget, None)
        else:
            index = self.insertTab(insert_at, widget, None)
        if not isinstance(icon, Button):
            btn = Button(label,
                         [icon] if icon is not None else None,
                         flat=True,
                         tooltip=tooltip)
            btn.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        else:
            btn = icon
        btn.setFixedSize(40, 40)
        btn.setIconSize(30, 30)
        btn.setContentsMargins(5, 5, 5, 5)
        btn.pressed.connect(lambda: self.setCurrentIndex(index))
        self.tab_bar.setTabButton(index, TAB_BTN_POS, btn)
        self.tab_bar.setTabToolTip(index, btn.toolTip())
        return index


    @QtCore.pyqtSlot(int, int)
    def moveTab(self, fromIndex: int, toIndex: int):
        widget = self.widget(fromIndex)
        button: Button | None = self.tab_bar.tabButton(fromIndex, TAB_BTN_POS)  # type: ignore
        self.tab_bar.setTabButton(fromIndex, TAB_BTN_POS, None)
        icon = self.tabIcon(fromIndex)
        text = self.tabText(fromIndex)

        self.removeTab(fromIndex)
        if button:
            self.addTabCustom(widget, text, button, insert_at=toIndex)
        else:
            self.insertTab(toIndex, widget, icon, text)
        self.setCurrentIndex(toIndex)

    @QtCore.pyqtSlot(int, QtCore.QPoint)
    def detachTab(self, index: int, point: QtCore.QPoint):
        name = self.tabText(index)
        icon = self.tabIcon(index)
        button: Button | None = self.tab_bar.tabButton(index, TAB_BTN_POS)  # type: ignore
        self.tab_bar.setTabButton(index, TAB_BTN_POS, None)
        if icon.isNull() and button is None:
            icon = self.window().windowIcon()  # type: ignore
        contentWidget = self.widget(index)
        # button = button or icon
        if not contentWidget:
            return
        contentWidgetRect = contentWidget.frameGeometry()
        # Create a new detached tab window
        detachedTab = DetachedTab(name, contentWidget, button)
        detachedTab.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        # detachedTab.setWindowIcon(icon)
        detachedTab.setGeometry(contentWidgetRect)
        # detachedTab.resize(600, 600)
        detachedTab.onCloseSignal.connect(self.attachTab)
        detachedTab.onDropSignal.connect(self.tab_bar.detachedTabDrop)
        detachedTab.move(point)
        detachedTab.show()
        tab_id = str(uuid4())
        detachedTab.setObjectName(tab_id)
        # Create a reference to maintain access to the detached tab
        self.detachedTabs[tab_id] = detachedTab

    def attachTab(self, contentWidget, tab_id: str, name: str,
                  icon: Button | None, insertAt=None):
        old_index = None
        if hasattr(contentWidget, '_initial_tab_index'):
            old_index = getattr(contentWidget, '_initial_tab_index')
        contentWidget.setParent(self)
        del self.detachedTabs[tab_id]
        if icon is None:
            if insertAt is None:
                index = self.addTab(contentWidget, name)
            else:
                index = self.insertTab(insertAt, contentWidget, name)
        else:
            index: int = self.addTabCustom(contentWidget, name, icon,
                                           insert_at=old_index)
        if index > -1:
            self.setCurrentIndex(index)
        self.sort_tabs()

    def _get_index_order(self):
        index_order = {}
        for current_index in range(self.count()):
            if hasattr(self.widget(current_index), '_initial_tab_index'):
                initial_index = getattr(self.widget(current_index), '_initial_tab_index')
                if initial_index != current_index:
                    index_order[initial_index] = current_index
        return index_order

    def sort_tabs(self):
        index_order = self._get_index_order()
        if not index_order:
            return
        initial_index = list(index_order.keys())[0]
        from_index = index_order.pop(initial_index)
        to_index = initial_index
        if self.widget(to_index):
            self.moveTab(from_index, to_index)
        else:
            self.moveTab(from_index, abs((self.count() - 1) - to_index))
        if len(index_order):
            return self.sort_tabs()


    def removeTabByName(self, name):
        attached = False
        for index in range(self.count()):
            if str(name) == str(self.tabText(index)):
                self.removeTab(index)
                attached = True
                break
        if not attached:
            for key in self.detachedTabs:
                if str(name) == str(key):
                    self.detachedTabs[key].onCloseSignal.disconnect()
                    self.detachedTabs[key].close()
                    del self.detachedTabs[key]
                    break

    @QtCore.pyqtSlot(str, int, QtCore.QPoint)
    def detachedTabDrop(self, tab_id: str, index: int, dropPos: QtCore.QPoint):
        tabDropPos = self.mapFromGlobal(dropPos)
        if tabDropPos in self.tab_bar.rect():
            self.detachedTabs[tab_id].close()
            # self.moveTab(self.tab_bar.count() - 1, index)

    def closeEvent(self, a0: QtGui.QCloseEvent | None) -> None:
        self.closeDetachedTabs()
        return super().closeEvent(a0)

    def closeDetachedTabs(self):
        detached_tabs: list = sorted(self.detachedTabs.values(),
                                     key=lambda x: x.contentWidget._initial_tab_index,
                                     reverse=True)
        for tab in detached_tabs:
            tab.close()

    def freeze_tabs(self):
        for i in range(self.count()):
            setattr(self.widget(i), '_initial_tab_index', i)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setStyleSheet(stylesheet)
    dark()
    # QtWidgets.QApplication.setStyle(ProxyStyle())
    w = TabWidget('right')
    assets = Path(__file__).parents[1] / 'assets' / 'svg'
    w.addTabCustom(QtWidgets.QLineEdit('First tab'), "", assets / 'register.svg', 'First tab')
    w.addTabCustom(QtWidgets.QLineEdit('Second tab'), "", assets / 'bell.svg', 'Second tab')
    w.addTabCustom(QtWidgets.QLineEdit('Third tab'), "", assets / 'camera.svg', 'Third tab')
    w.freeze_tabs()
    # w.addTab(QtWidgets.QLineEdit('First tab'),  "First tab")
    # w.addTab(QtWidgets.QLineEdit('Second tab'), "Second tab")
    # w.addTab(QtWidgets.QLineEdit('Third tab'),  "Third tab")
    # w.tab_bar.setTabIcon(0, QtGui.QIcon(str(assets / 'register.svg')))
    w.set_active_tab(0)
    w.resize(640, 480)
    w.show()

    app.exec()