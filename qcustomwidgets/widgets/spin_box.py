from PyQt6 import QtWidgets, QtGui, QtCore


class SpinBox(QtWidgets.QAbstractSpinBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.editingFinished.connect(self.on_editing_finished)
        self.last_valid_val: int = 0
        self._line_edit: QtWidgets.QLineEdit = self.lineEdit()  # type: ignore
        self.step_size: int = 1
        self.min_val: int = 0
        self.max_val: int = 0xFFFFFFFF
        self.is_hex_mode: bool = False
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self,
                                           self.toggle_hex_mode,
                                           context=QtCore.Qt.ShortcutContext.WidgetShortcut)

    def toggle_hex_mode(self) -> None:
        self.is_hex_mode = not self.is_hex_mode
        self._set_val(self.last_valid_val)

    def stepEnabled(self) -> QtWidgets.QAbstractSpinBox.StepEnabledFlag:
        if self.last_valid_val != self.max_val and self.last_valid_val != self.min_val:
            return super().StepEnabledFlag.StepDownEnabled | super().StepEnabledFlag.StepUpEnabled
        elif self.last_valid_val == self.max_val:
            return super().StepEnabledFlag.StepDownEnabled
        elif self.last_valid_val == self.min_val:
            return super().StepEnabledFlag.StepUpEnabled
        else:
            return super().StepEnabledFlag.StepNone

    def on_editing_finished(self) -> None:
        text: str = self.text()
        try:
            val = eval(text)
            if isinstance(val, (int, float)):
                self.setValue(int(val))
            else:
                raise ValueError
        except Exception:
            self._set_val(self.last_valid_val)

    def _set_val(self, val: int) -> None:
        if self.is_hex_mode:
            if val > 0:
                self._line_edit.setText(f'0x{val:02X}')
            else:
                self._line_edit.setText(f'- 0x{-val:02X}')
        else:
            self._line_edit.setText(f'{val}')

    def focusOutEvent(self, e: QtGui.QFocusEvent | None) -> None:
        self.on_editing_finished()
        return super().focusOutEvent(e)

    def stepBy(self, steps: int) -> None:
        if self.min_val <= self.last_valid_val + steps <= self.max_val:
            self.last_valid_val += steps
            self._set_val(self.last_valid_val)

    def setRange(self, min_val: int, max_val: int) -> None:
        self.setMinimum(min_val)
        self.setMaximum(max_val)

    def setMinimum(self, min_val: int) -> None:
        self.min_val = min_val

    def setMaximum(self, max_val: int) -> None:
        self.max_val = max_val

    def setValue(self, val: int) -> None:
        if self.min_val <= val <= self.max_val:
            self.last_valid_val = val
            self._set_val(val)

    def value(self) -> int:
        return self.last_valid_val


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = QtWidgets.QWidget()
    _l = QtWidgets.QVBoxLayout(w)
    w.setLayout(_l)
    _l.addWidget(SpinBox())
    _l.addWidget(SpinBox())
    _l.addWidget(QtWidgets.QSpinBox())
    w.show()
    app.exec()