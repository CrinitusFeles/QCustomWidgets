from PyQt6 import QtWidgets, QtGui
from PyQt6.QtGui import QPalette, QColor


def dark() -> None:
    p = QtGui.QPalette()
    # base
    p.setColor(QPalette.ColorRole.WindowText, QColor('#B4B4B4'))
    p.setColor(QPalette.ColorRole.Button, QColor('#353535'))
    p.setColor(QPalette.ColorRole.Light, QColor('#B4B4B4'))
    p.setColor(QPalette.ColorRole.Midlight, QColor('#5A5A5A'))
    p.setColor(QPalette.ColorRole.Dark, QColor('#232323'))
    p.setColor(QPalette.ColorRole.Text, QColor('#B4B4B4'))
    p.setColor(QPalette.ColorRole.BrightText, QColor('#B4B4B4'))
    p.setColor(QPalette.ColorRole.ButtonText, QColor('#B4B4B4'))
    p.setColor(QPalette.ColorRole.Base, QColor('#2A2A2A'))
    p.setColor(QPalette.ColorRole.Window, QColor('#353535'))
    p.setColor(QPalette.ColorRole.Shadow, QColor('#141414'))
    p.setColor(QPalette.ColorRole.Highlight, QColor('#2A82DA'))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor('#B4B4B4'))
    p.setColor(QPalette.ColorRole.Link, QColor('#38FCC4'))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor('#424242'))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor('#353535'))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor('#B4B4B4'))

    # disabled
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.WindowText, QColor('#7F7F7F'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.Text, QColor('#7F7F7F'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.ButtonText, QColor('#7F7F7F'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.Highlight, QColor('#505050'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.HighlightedText, QColor('#7F7F7F'))

    QtWidgets.QApplication.setPalette(p)
    QtWidgets.QApplication.setStyle('Fusion')


def light() -> None:
    p = QtGui.QPalette()

    # base
    p.setColor(QPalette.ColorRole.WindowText, QColor('#000000'))
    p.setColor(QPalette.ColorRole.Button, QColor('#F0F0F0'))
    p.setColor(QPalette.ColorRole.Light, QColor('#B4B4B4'))
    p.setColor(QPalette.ColorRole.Midlight, QColor('#C8C8C8'))
    p.setColor(QPalette.ColorRole.Dark, QColor('#FFFFFF'))
    p.setColor(QPalette.ColorRole.Text, QColor('#000000'))
    p.setColor(QPalette.ColorRole.BrightText, QColor('#000000'))
    p.setColor(QPalette.ColorRole.ButtonText, QColor('#000000'))
    p.setColor(QPalette.ColorRole.Base, QColor('#EDEDED'))
    p.setColor(QPalette.ColorRole.Window, QColor('#F0F0F0'))
    p.setColor(QPalette.ColorRole.Shadow, QColor('#141414'))
    p.setColor(QPalette.ColorRole.Highlight, QColor('#4CA3E0'))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor('#000000'))
    p.setColor(QPalette.ColorRole.Link, QColor('#00A2E8'))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor('#FFFFFF'))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor('#F0F0F0'))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor('#000000'))

    # disabled
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.WindowText, QColor('#737373'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.Text, QColor('#737373'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.ButtonText, QColor('#737373'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.Highlight, QColor('#BEBEBE'))
    p.setColor(QPalette.ColorGroup.Disabled,
               QPalette.ColorRole.HighlightedText, QColor('#737373'))

    QtWidgets.QApplication.setPalette(p)
    QtWidgets.QApplication.setStyle('Fusion')
