from PyQt6 import QtWidgets, QtGui, QtCore
class MySpinBox(QtWidgets.QAbstractSpinBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.editingFinished.connect(self.on_editing_finished)
        self.last_valid_val: int = 0
        self._line_edit: QtWidgets.QLineEdit = self.lineEdit()  # type: ignore
        self.step_size: int = 1
        self.min_val: int = 0
        self.max_val: int = 999999

    # def mousePressEvent(self,  e):
    #     super().mousePressEvent(e)
    #     if e:
    #         opt = QtWidgets.QStyleOptionSpinBox()
    #         self.initStyleOption(opt)
    #         control = self.style().hitTestComplexControl(  # type: ignore
    #             QtWidgets.QStyle.ComplexControl.CC_SpinBox, opt, e.pos(), self
    #         )
    #         if control == QtWidgets.QStyle.SubControl.SC_SpinBoxUp:
    #             # self.upClicked.emit()
    #             self.stepBy(self.step_size)
    #         elif control == QtWidgets.QStyle.SubControl.SC_SpinBoxDown:
    #             # self.downClicked.emit()
    #             self.stepBy(-self.step_size)

    def stepEnabled(self) -> QtWidgets.QAbstractSpinBox.StepEnabledFlag:
        super().stepEnabled()
        if self.last_valid_val != self.max_val and self.last_valid_val != self.min_val:
            return super().StepEnabledFlag.StepDownEnabled | super().StepEnabledFlag.StepUpEnabled
        elif self.last_valid_val == self.max_val:
            return super().StepEnabledFlag.StepDownEnabled
        elif self.last_valid_val == self.max_val:
            return super().StepEnabledFlag.StepUpEnabled
        else:
            return super().StepEnabledFlag.StepNone

    def on_editing_finished(self):
        text = self.text()
        try:
            val = eval(text)
            if isinstance(val, (int, float)) and self.min_val <= val <= self.max_val:
                self._line_edit.setText(f'{int(val)}')
                self.last_valid_val = int(val)
            else:
                raise ValueError
        except Exception:
            self._line_edit.setText(f'{self.last_valid_val}')

    def focusOutEvent(self, e: QtGui.QFocusEvent | None) -> None:
        self.on_editing_finished()
        return super().focusOutEvent(e)

    def wheelEvent(self, e: QtGui.QWheelEvent | None) -> None:
        if e:
            steps = 1 if e.angleDelta().y() > 0 else -1
            if self.min_val <= self.last_valid_val + steps <= self.max_val:
                self.last_valid_val += steps
                self._line_edit.setText(f'{self.last_valid_val}')
        return super().wheelEvent(e)

    def stepBy(self, steps: int) -> None:
        if self.min_val <= self.last_valid_val + steps <= self.max_val:
            self.last_valid_val += steps
            self._line_edit.setText(f'{self.last_valid_val}')
        super().stepBy(steps)

    def keyPressEvent(self, e: QtGui.QKeyEvent | None):
        if e:
            if e.key() == QtCore.Qt.Key.Key_Up:
                self.stepUp()
            elif e.key() == QtCore.Qt.Key.Key_Down:
                self.stepDown()
        super().keyPressEvent(e)

    def setRange(self, min_val: int, max_val: int):
        self.setMinimum(min_val)
        self.setMaximum(max_val)

    def setMinimum(self, min_val: int):
        self.min_val = min_val

    def setMaximum(self, max_val: int):
        self.max_val = max_val


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = QtWidgets.QWidget()
    _l = QtWidgets.QVBoxLayout(w)
    w.setLayout(_l)
    _l.addWidget(MySpinBox())
    _l.addWidget(MySpinBox())
    _l.addWidget(QtWidgets.QSpinBox())
    w.show()
    app.exec()