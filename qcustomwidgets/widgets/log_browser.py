from PyQt6 import QtWidgets, QtCore


class LogBrowser(QtWidgets.QTextBrowser):
    def __init__(self) -> None:
        super().__init__()
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

    def show_context_menu(self, point):
        menu = self.createStandardContextMenu()
        if menu:
            menu.addAction('Clear all').setObjectName('clear')  # type: ignore
            ret = menu.exec(self.mapToGlobal(point))
            if ret:
                obj = ret.objectName()
                if obj == 'clear':
                    self.clear()