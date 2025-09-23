import asyncio
from functools import partial
from pathlib import Path
from typing_extensions import override
import weakref
from PyQt6.uic.load_ui import loadUi
from PyQt6.QtGui import QPaintEvent, QPainter, QIcon, QPalette, QPixmap, QColor
from PyQt6.QtCore import (Qt, QPoint, QSize, QEvent, QTimer,
                          QPropertyAnimation, QParallelAnimationGroup,
                          QEasingCurve, QObject, pyqtSignal)
from PyQt6.QtWidgets import (QStyleOption, QWidget, QStyle, QLabel, QPushButton,
                            QGraphicsDropShadowEffect, QScrollArea,
                            QGraphicsOpacityEffect, QApplication, QVBoxLayout)
from qasync import QEventLoop


class BaseModal(QWidget):
    iconlabel: QLabel
    titlelabel: QLabel
    bodyLabel: QLabel
    closeButton: QPushButton
    verticalLayout_2: QVBoxLayout
    position: str = ''
    title: str | None = None
    description: str | None = None
    modalIcon: QPixmap | None = None
    isClosable = True
    animationDuration = 1500

    margin = 24
    spacing = 16

    closedSignal = pyqtSignal()

    commonStyle = ("""
            * {
                border-radius: 10px;
                border-width: 0px;
            }
            QPushButton#closeButton{
                font-weight: 1000;
                min-width: 20px;
                min-height: 20px;
                max-width: 20px;
                max-height: 20px;
            }
            QLabel#iconlabel{
                min-width: 20px;
                min-height: 20px;
                max-width: 20px;
                max-height: 20px;
            }
        """)

    def __init__(self, position: str = '', title: str | None = None,
                 description: str | None = None, **kwargs):
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('info.ui'), self)
        style = self.style()
        if not style:
            raise RuntimeError('No style')
        # get default icon:
        icon_path: Path = Path(__file__).parents[1].joinpath('assets')
        self.closeIcon: QIcon = QIcon(str(icon_path.joinpath('close_mini.svg')))# style.standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        self.closeButton.setIcon(self.closeIcon)

        # Get the info icon from the style
        self.infoIcon: QPixmap = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation).pixmap(QSize(32, 32))
        # Get the success icon from the style
        success_icon = QPixmap(str(icon_path.joinpath('cloud-done.svg')))
        self.successIcon: QPixmap = success_icon  # style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton).pixmap(QSize(32, 32))
        # Get the warning icon from the style
        self.warningIcon: QPixmap = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning).pixmap(QSize(32, 32))
        # Get the error icon from the style
        self.errorIcon: QPixmap = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical).pixmap(QSize(32, 32))

        # Customize modal based on kwargs
        self.titlelabel.setText(title or '')
        self.bodyLabel.setText(description or '')

        if 'closeIcon' in kwargs:
            # Set icon
            self.closeIcon = QIcon(kwargs['closeIcon'])
            self.closeButton.setIcon(self.closeIcon)

        if 'modalIcon' in kwargs:
            # Set modal icon
            self.modalIcon = QPixmap(kwargs['modalIcon'])
            self.iconlabel.setPixmap(self.modalIcon)

        if "isClosable"  in kwargs:
            self.isClosable = kwargs['isClosable']

        if 'parent' in kwargs:
            self.setParent(kwargs['parent'])
        parent: QWidget | None = self.parent()  # type: ignore
        if parent is not None:
            palette = parent.palette()
        else:
            # Get the existing QApplication instance (if it exists)
            app = QApplication.instance()
            # If no QApplication instance exists, create one
            if app is None:
                app = QApplication([])
            # Get the palette from the application
            palette = app.palette()  # type: ignore

        background_color = palette.color(QPalette.ColorRole.Window)

        # Calculate the luminance of the background color
        luminance: float = 0.2126 * background_color.red()
        luminance += 0.7152 * background_color.green()
        luminance += 0.0722 * background_color.blue()

        shadow_effect = QGraphicsDropShadowEffect(self)
        # shadow_effect.setBlurRadius(100)
        shadow_effect.setColor(QColor(0, 0, 0, 50))
        shadow_effect.setOffset(10, 10)
        self.setGraphicsEffect(shadow_effect)

        # Determine if the background color is dark or light
        if luminance < 128:
            # Dark background
            self.isDark = True
        else:
            # Light background
            self.isDark = False

        self.position = position
        if 'animationDuration' in kwargs:
            self.animationDuration = kwargs['animationDuration']
        if 'duration' in kwargs:
            self.animationDuration = kwargs['duration']

        self.closeButton.setFixedSize(20, 20)
        self.closeButton.setIconSize(QSize(self.spacing, self.spacing))
        self.closeButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setVisible(self.isClosable)

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(
            self.opacityEffect, b'opacity', self)  # type: ignore

        # Set attribute to enable styled background
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    @override
    def paintEvent(self, a0: QPaintEvent | None):
        super().paintEvent(a0)

        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget,  # type: ignore
                                    opt, painter, self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        #
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 6, 6)

    def adjustSizeToContent(self):
        # Calculate the size hint based on the content
        content_size = self.layout().sizeHint()  # type: ignore
        # Add some padding if needed
        padding = 0
        self.setFixedSize(content_size.width() + padding,
                          content_size.height() + padding)
        parent: QWidget | None = self.parent()  # type: ignore
        if not parent:
            return
        if self.position == 'top-right':
            x: int = parent.size().width() - self.width() - self.margin
            # Adjust x-position to have a 20-pixel margin
            self.move(x, self.pos().y())

        elif self.position == 'top-center':
            x = (parent.size().width() - self.width()) // 2
            self.move(x, self.pos().y())

        elif self.position == 'top-left':
            x = self.margin
            self.move(x, self.pos().y())

        elif self.position == 'center-center':
            x = (parent.size().width() - self.width()) // 2
            y: int = (parent.size().height() - self.height()) // 2
            self.move(x, y)

        elif self.position == 'center-right':
            x = parent.size().width() - self.width() - self.margin
            y = (parent.size().height() - self.height()) // 2
            self.move(x, y)

        elif self.position == 'center-left':
            x = self.margin
            y = (parent.size().height() - self.height()) // 2
            self.move(x, y)

        elif self.position == 'bottom-right':
            x = parent.size().width() - self.width() - self.margin
            y = parent.size().height() - self.height() - self.margin
            self.move(x, y)

        elif self.position == 'bottom-left':
            x = self.margin
            y = parent.size().height() - self.height() - self.margin
            self.move(x, y)


    def fadeOut(self):
        """ fade out """
        if self.animationDuration < 0:
            return
        self.opacityAni.setDuration(self.animationDuration - 500)
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.finished.connect(self.close)
        self.opacityAni.start()

    @override
    def eventFilter(self, a0, a1: QEvent | None) -> bool:
        if a0 is self.parent() and a1:
            if a1.type() in [QEvent.Type.Resize,
                            QEvent.Type.WindowStateChange]:
                self.adjustSizeToContent()

        return super().eventFilter(a0, a1)

    @override
    def closeEvent(self, a0) -> None:
        self.closedSignal.emit()
        self.deleteLater()

    @override
    def showEvent(self, a0) -> None:
        super().showEvent(a0)

        self.adjustSizeToContent()

        if self.animationDuration > 0:
            QTimer.singleShot(self.animationDuration, self.fadeOut)

        if self.position is not None:
            manager = ModalsManager.make(self.position)
            manager.add(self)
        parent = self.parent()
        if parent:
            parent.installEventFilter(self)

    def parent(self):
        p = super().parent()
        if not p:
            raise ValueError('Modal window without parent')
        return p

    def setIcon(self, icon):
        self.icon = icon
        if isinstance(icon, QIcon):
            pixmap = icon.pixmap(QSize(32, 32))
            self.iconlabel.setPixmap(pixmap)
        elif isinstance(icon, str):
            # Assuming icon is a path to an image file
            pixmap = QPixmap(icon).scaled(QSize(32, 32))
            self.iconlabel.setPixmap(pixmap)
        else:
            self.iconlabel.hide()

    # def setDescription(self, description) -> None:
    #     self.description = description
    #     if not self.description:
    #         self.description.hide()
    #         return
    #     self.bodyLabel.setText(description)
    #     self.adjustSizeToContent()

    def setTitle(self, title) -> None:
        self.title = title
        if not self.title:
            self.titlelabel.hide()
            return
        self.titlelabel.setText(title)
        self.adjustSizeToContent()

    def addWidget(self, widget) -> None:
        self.widget = widget
        if self.widget:
            self.verticalLayout_2.addWidget(self.widget)


class InformationModal(BaseModal):
    def __init__(self, position: str = 'top-center',
                 title: str | None = 'Info',
                 description: str | None = None, **kwargs):
        super().__init__(position, title, description, **kwargs)
        self.setWindowTitle("Information")
        if self.modalIcon:
            self.iconlabel.setPixmap(self.modalIcon)
        else:
            self.iconlabel.setPixmap(self.infoIcon)

        lightStyle = """
            /* Information Modal */
            InformationModal {
                background-color: #E6F7FF; /* Light blue or teal */
            }
            InformationModal * {
                color: #333333;
                background-color: transparent;
            }
        """

        darkStyle = """
            InformationModal {
                background-color: #2799be; /* Light blue or teal for improved contrast */
            }
            InformationModal * {
                color: #F5F5F5; /* Whitish color */
                background-color: transparent;
            }
        """

        if self.isDark:
            self.setStyleSheet(darkStyle + self.commonStyle)
        else:
            self.setStyleSheet(lightStyle + self.commonStyle)


class SuccessModal(BaseModal):
    def __init__(self, position: str = 'top-center',
                 title: str | None = 'Success',
                 description: str | None = None, **kwargs):
        super().__init__(position, title, description, **kwargs)
        self.setWindowTitle("Success")
        if self.modalIcon:
            self.iconlabel.setPixmap(self.modalIcon)
        else:
            self.iconlabel.setPixmap(self.successIcon)

        lightStyle = """
            /* Success Modal */
            SuccessModal {
                background-color: #81c785; /* Light green */
            }
            SuccessModal * {
                color: #FFFFFF; /* Dark green or gray */
                background-color: transparent;
            }
        """
        darkStyle = """
            /* Success Modal */
            SuccessModal {
                background-color: #81c785; /* Dark green for improved contrast */
            }
            SuccessModal * {
                color: #FFFFFF; /* Whitish color */
                background-color: transparent;
            }
        """
        if self.isDark:
            self.setStyleSheet(darkStyle + self.commonStyle)
        else:
            self.setStyleSheet(lightStyle + self.commonStyle)


class WarningModal(BaseModal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("Warning")
        if self.modalIcon:
            self.iconlabel.setPixmap(self.modalIcon)
        else:
            self.iconlabel.setPixmap(self.warningIcon)

        lightStyle = """
            /* Warning Modal */
            WarningModal {
                background-color: #FFF9E1; /* Light yellow */
            }
            WarningModal * {
                color: #333333; /* Dark yellow or gray */
                background-color: transparent;
            }
        """
        darkStyle = """
            /* Warning Modal */
            WarningModal {
                background-color: #bb8128; /* Light yellow for improved contrast */
            }
            WarningModal * {
                color: #F5F5F5; /* Whitish color */
                background-color: transparent;
            }
        """
        if self.isDark:
            self.setStyleSheet(darkStyle + self.commonStyle)
        else:
            self.setStyleSheet(lightStyle + self.commonStyle)


class ErrorModal(BaseModal):
    def __init__(self, position: str = 'top-center',
                 title: str | None = 'Error',
                 description: str | None = None, **kwargs):
        super().__init__(position, title, description, **kwargs)
        self.setWindowTitle("Error")
        if self.modalIcon:
            self.iconlabel.setPixmap(self.modalIcon)
        else:
            self.iconlabel.setPixmap(self.errorIcon)

        lightStyle = """
            /* Error Modal */
            ErrorModal {
                background-color: #FFEBEE; /* Light red or pink */
            }
            ErrorModal * {
                color: #333333; /* Dark red or gray */
                background-color: transparent;
            }
        """
        darkStyle = """
            /* Error Modal */
            ErrorModal {
                background-color: #bb221d; /* Light red or pink for improved contrast */
            }
            ErrorModal * {
                color: #F5F5F5; /* Whitish color */
                background-color: transparent;
            }
        """
        if self.isDark:
            self.setStyleSheet(darkStyle + self.commonStyle)
        else:
            self.setStyleSheet(lightStyle + self.commonStyle)


class CustomModal(BaseModal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("Custom")
        if self.modalIcon:
            self.iconlabel.setPixmap(QPixmap(self.modalIcon))

        style = """
            CustomModal * {
                background-color: transparent;
            }
        """

        self.setStyleSheet(style)


class ModalsManager(QObject):
    _instance = None
    managers = {}

    # def __new__(cls, *args, **kwargs):
    #     # Singleton pattern: ensures only one instance of the class is created
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls, *args, **kwargs)
    #         cls._instance.__initialized = False

    #     return cls._instance

    def __init__(self):
        # Initialize the class attributes and instance variables
        # if self.__initialized:
        #     return

        super().__init__()
        self.spacing = 16
        self.margin = 24
        self.modals_store = weakref.WeakKeyDictionary()
        self.aniGroups = weakref.WeakKeyDictionary()       # Dictionary to hold animation groups
        self.slideAnis = []  # List to hold slide animations
        self.dropAnis = []   # List to hold drop animations
        self.__initialized = True

    def add(self, modal: BaseModal):
        """Add an info bar"""
        p = modal.parent()    # Get the parent widget
        if not p:
            return

        # Initialize dictionaries if the parent widget is not already in them
        if p not in self.modals_store:
            p.installEventFilter(self)  # Install event filter on parent widget
            self.modals_store[p] = [] # List to hold modal instances for this parent
            self.aniGroups[p] = QParallelAnimationGroup(self) # Animation group for this parent

        # Check if the modal instance already exists for this parent
        if modal in self.modals_store[p]:
            return

        # Add drop animation if there are already existing modal instances for this parent
        if self.modals_store[p]:
            dropAni = QPropertyAnimation(modal, b'pos')  # type: ignore # Create a drop animation
            dropAni.setDuration(200)  # Set the duration of the animation

            self.aniGroups[p].addAnimation(dropAni)  # Add the drop animation to the animation group
            self.dropAnis.append(dropAni)           # Add the drop animation to the list

            modal.setProperty('dropAni', dropAni)  # Set a property to hold the drop animation

        # Add slide animation
        self.modals_store[p].append(modal)    # Add the modal instance to the list
        slideAni: QPropertyAnimation = self.createSlideAni(modal)  # Create a slide animation
        self.slideAnis.append(slideAni)                 # Add the slide animation to the list

        modal.setProperty('slideAni', slideAni)  # Set a property to hold the slide animation
        modal.closedSignal.connect(lambda: self.remove(modal))  # Connect close signal to remove method

        slideAni.start()  # Start the slide animation

    def remove(self, modal: BaseModal):
        """Remove an info bar"""
        p = modal.parent()  # Get the parent widget
        if p not in self.modals_store:
            return

        if modal not in self.modals_store[p]:
            return

        # Remove the modal instance from the list
        self.modals_store[p].remove(modal)

        # Remove drop animation
        dropAni: QPropertyAnimation = modal.property('dropAni')   # Get the drop animation property
        if dropAni:
            self.aniGroups[p].removeAnimation(dropAni)  # Remove the drop animation from the animation group
            self.dropAnis.remove(dropAni)              # Remove the drop animation from the list

        # Remove slide animation
        slideAni: QPropertyAnimation = modal.property('slideAni') # Get the slide animation property
        if slideAni:
            self.slideAnis.remove(slideAni)  # Remove the slide animation from the list

        # Adjust the position of the remaining info bars
        self.updateDropAni(p)
        self.aniGroups[p].start()  # Start the animation group

    def createSlideAni(self, modal: BaseModal):
        """Create a slide animation for the given modal"""
        slideAni = QPropertyAnimation(modal, b'pos')  # type: ignore # Create a slide animation

        # Set easing curve for smooth animation
        easing_curve = QEasingCurve.Type.OutCubic
        slideAni.setEasingCurve(easing_curve)

        slideAni.setDuration(200)  # Set the duration of the animation

        # Set initial position and end value for the animation
        start_pos: QPoint = self.slideStartPos(modal)
        end_pos: QPoint = self.modalPosition(modal)

        # Ensure that the initial position is set correctly
        modal.move(start_pos)

        # Set start and end values for the animation
        slideAni.setStartValue(start_pos)
        slideAni.setEndValue(end_pos)

        return slideAni

    def updateDropAni(self, parent):
        """Update drop animation for the remaining info bars"""
        for bar in self.modals_store[parent]:
            ani: QPropertyAnimation = bar.property('dropAni')  # Get the drop animation property
            if not ani:
                continue

            ani.setStartValue(bar.pos())   # Set the start value of the animation
            ani.setEndValue(self.modalPosition(bar))  # Set the end value of the animation

    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None) -> QPoint:
        """Return the position of the modal"""
        # position = QCustomModals.position

        # if position == 'top-right':
        #     x: int = parentSize.width() - QCustomModals.width() - self.margin
        #     y: int = self.margin
        # elif position == 'top-center':
        #     x = (parentSize.width() - QCustomModals.width()) // 2
        #     y = self.margin
        # elif position == 'top-left':
        #     x = self.margin
        #     y = self.margin
        # elif position == 'center-center':
        #     x = (parentSize.width() - QCustomModals.width()) // 2
        #     y = (parentSize.height() - QCustomModals.height()) // 2
        # elif position == 'center-right':
        #     x = parentSize.width() - QCustomModals.width() - self.margin
        #     y = (parentSize.height() - QCustomModals.height()) // 2
        # elif position == 'center-left':
        #     x = self.margin
        #     y = (parentSize.height() - QCustomModals.height()) // 2
        # elif position == 'bottom-right':
        #     x = parentSize.width() - QCustomModals.width() - self.margin
        #     y = parentSize.height() - QCustomModals.height() - self.margin
        # elif position == 'bottom-left':
        #     x = self.margin
        #     y = parentSize.height() - QCustomModals.height() - self.margin
        # elif position == 'bottom-center':
        #     x = (parentSize.width() - QCustomModals.width()) // 2
        #     y = parentSize.height() - QCustomModals.height() - self.margin
        # else:
        #     # Default to top-right position if position is not recognized
        #     x = parentSize.width() - QCustomModals.width() - self.margin
        #     y = self.margin

        # return QPoint(x, y)
        ...


    def slideStartPos(self, modal: BaseModal) -> QPoint:
        """Return the start position of slide animation"""
        # if QCustomModals.position.startswith('top'):
        #     return QPoint(QCustomModals.pos().x(), -QCustomModals.height())
        # elif QCustomModals.position.startswith('center'):
        #     return QPoint(QCustomModals.pos().x(),
        #                   QCustomModals.parent().height())  # type: ignore
        # elif QCustomModals.position.startswith('bottom'):
        #     return QPoint(QCustomModals.pos().x(),
        #                   QCustomModals.parent().height() + QCustomModals.height())  # type: ignore
        # else:
        #     # Default to top position if position is not recognized
        #     return QPoint(self.pos().x(), -self.height())
        ...

    @override
    def eventFilter(self, a0, a1: QEvent | None):
        """Event filter to handle resize and window state change events"""
        if a0 not in self.modals_store:
            return False

        if a1 and a1.type() in [QEvent.Type.Resize, QEvent.Type.WindowStateChange]:
            if a1.type() == QEvent.Type.Resize:
                size = a1.size()  # type: ignore
            else:
                size = None
            for bar in self.modals_store[a0]:
                bar.move(self.modalPosition(bar, size))

        return super().eventFilter(a0, a1)

    @classmethod
    def register(cls, name: str):
        """Register menu animation manager"""
        def wrapper(Manager):
            if name not in cls.managers:
                cls.managers[name] = Manager

            return Manager

        return wrapper

    @classmethod
    def make(cls, position: str):
        """Create info bar manager according to the display position"""
        if position not in cls.managers:
            raise ValueError(f'`{position}` is an invalid animation type.')

        return cls.managers[position]()

@ModalsManager.register("center-center")
class CenterCenterQCustomModalsManager(ModalsManager):
    """Center position info bar manager"""

    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None):
        p: QWidget = modal.parent()  # type: ignore
        if parentSize is not None:
            pSize = parentSize
        else:
            pSize = p.size()

        x = (pSize.width() - modal.width()) // 2
        y = (pSize.height() - modal.height()) // 2

        return QPoint(x, y)

    @override
    def slideStartPos(self, modal: BaseModal) -> QPoint:
        """Calculate the start position of slide animation for center-center"""
        return QPoint(modal.pos().x(), -modal.height())


@ModalsManager.register("top-center")
class TopModalsManager(ModalsManager):
    """ Top position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None) -> QPoint:
        p: QWidget = modal.parent()  # type: ignore

        x = (p.width() - modal.width()) // 2
        y = self.margin
        index = self.modals_store[p].index(modal)
        for bar in self.modals_store[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(x, y)

    @override
    def slideStartPos(self, modal: BaseModal):
       return QPoint(modal.pos().x(), -modal.height())


@ModalsManager.register("top-right")
class TopRightModalsManager(ModalsManager):
    """ Top right position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None) -> QPoint:
        p: QWidget = modal.parent()  # type: ignore
        if parentSize is not None:
            pSize = parentSize
        else:
            pSize = p.size()

        x: int = pSize.width() - modal.width() - self.margin
        y: int = self.margin
        index = self.modals_store[p].index(modal)
        for bar in self.modals_store[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(x, y)

    @override
    def slideStartPos(self, modal: BaseModal):
        return QPoint(modal.parent().width(),  # type: ignore
                      self.modalPosition(modal).y())


@ModalsManager.register("bottom-right")
class BottomRightQCustomModalsManager(ModalsManager):
    """ Bottom right position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None) -> QPoint:
        p: QWidget = modal.parent()  # type: ignore
        if parentSize is not None:
            pSize = parentSize
        else:
            pSize = p.size()

        x: int = pSize.width() - modal.width() - self.margin
        y: int = pSize.height() - modal.height() - self.margin

        index = self.modals_store[p].index(modal)
        for bar in self.modals_store[p][0:index]:
            y -= (bar.height() + self.spacing)

        return QPoint(x, y)

    @override
    def slideStartPos(self, modal: BaseModal):
        return QPoint(modal.parent().width(),  # type: ignore
                      self.modalPosition(modal).y())


@ModalsManager.register("top-left")
class TopLeftQCustomModalsManager(ModalsManager):
    """ Top left position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None) -> QPoint:
        p: QWidget = modal.parent()  # type: ignore

        y: int = self.margin
        index: int = self.modals_store[p].index(modal)

        for bar in self.modals_store[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(self.margin, y)

    @override
    def slideStartPos(self, modal: BaseModal):
        return QPoint(-modal.width(),
                      self.modalPosition(modal).y())


@ModalsManager.register("bottom-left")
class BottomLeftQCustomModalsManager(ModalsManager):
    """ Bottom left position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None):
        p: QWidget = modal.parent()  # type: ignore
        if parentSize is not None:
            pSize = parentSize
        else:
            pSize = p.size()

        y: int = pSize.height() - modal.height() - self.margin
        index: int = self.modals_store[p].index(modal)

        for bar in self.modals_store[p][0:index]:
            y -= (bar.height() + self.spacing)

        return QPoint(self.margin, y)

    @override
    def slideStartPos(self, modal: BaseModal):
        return QPoint(-modal.width(), self.modalPosition(modal).y())


@ModalsManager.register("bottom-center")
class BottomQCustomModalsManager(ModalsManager):
    """ Bottom position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None) -> QPoint:
        p: QWidget = modal.parent()  # type: ignore
        if parentSize is not None:
            pSize = parentSize
        else:
            pSize = p.size()

        x: int = (pSize.width() - modal.width()) // 2
        y: int = pSize.height() - modal.height() - self.margin
        index: int = self.modals_store[p].index(modal)

        for bar in self.modals_store[p][0:index]:
            y -= (bar.height() + self.spacing)

        return QPoint(x, y)

    @override
    def slideStartPos(self, modal: BaseModal):
        return QPoint(self.modalPosition(modal).x() + self.spacing,
                      self.modalPosition(modal).y())


@ModalsManager.register("center-left")
class CenterLeftQCustomModalsManager(ModalsManager):
    """ Center left position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None):
        p: QWidget = modal.parent()  # type: ignore
        if parentSize is not None:
            pSize = parentSize
        else:
            pSize = p.size()

        x: int = self.margin
        y: int = (pSize.height() - modal.height()) // 2

        return QPoint(x, y)

    @override
    def slideStartPos(self, modal):
        return QPoint(-modal.width(), modal.pos().y())


@ModalsManager.register("center-right")
class CenterRightQCustomModalsManager(ModalsManager):
    """ Center right position info bar manager """
    @override
    def modalPosition(self, modal: BaseModal,
                      parentSize: QSize | None = None) -> QPoint:
        p: QWidget = modal.parent()  # type: ignore
        if parentSize is not None:
            pSize = parentSize
        else:
            pSize = p.size()

        x: int = pSize.width() - modal.width() - self.margin
        y: int = (pSize.height() - modal.height()) // 2

        return QPoint(x, y)

    @override
    def slideStartPos(self, modal):
        return QPoint(modal.parent().width(),  # type: ignore
                      modal.pos().y())


# from PyQt6.QtMultimediaWidgets import QVideoWidget

class TestModalWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test Modal Window")
        # self.video = QVideoWidget(self)
        # self.video.setMinimumHeight(50)
        # self._layout.addWidget(self.video)
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self._layout.addWidget(self.scroll_area)

        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget)

        self.scroll_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.create_buttons()

    def create_buttons(self):
        modal_types: list[str] = ["Information", "Success", "Warning", "Error",
                                  "Custom"]
        positions: list[str] = ["top-left", "top-center", "top-right",
                                "center-left", "center-center", "center-right",
                                "bottom-left", "bottom-center", "bottom-right"]

        for modal_type in modal_types:
            for position in positions:
                button = QPushButton(f"{modal_type} Modal ({position})")
                button.setObjectName(f"{modal_type.lower()}_{position.replace('-', '_')}_button")
                button.setStyleSheet(f"background-color: {self.get_button_color(modal_type)}")
                button.clicked.connect(partial(self.show_modal, modal_type, position))
                self.scroll_layout.addWidget(button)

    def get_button_color(self, modal_type):
        if self.isDark():
            color_map = {
                "Information": "#2799be",  # dark blue or teal
                "Success": "#81c785",       # dark green
                "Warning": "#bb8128",       # dark yellow
                "Error": "#bb221d",         # dark red or pink
                "Custom": "#0E1115"         #
            }

        else:
            color_map = {
                "Information": "#E6F7FF",  # light blue or teal
                "Success": "#81c785",       # light green
                "Warning": "#FFF9E1",       # light yellow
                "Error": "#FFEBEE",         # light red or pink
                "Custom": "#FFFFFF"         #
            }
        return color_map.get(modal_type, "#FFFFFF")  # Default to white

    def show_modal(self, modal_type: str, position: str):
        kwargs = {
            "title": f"{modal_type} Title",
            "description": f"This is a {modal_type.lower()} modal in "\
                           f"position: {position}",
            "position": position,
            "parent": self,
            "animationDuration": 1400 # set to zero if you want you modal to not auto-close
        }
        modal = QWidget()
        if modal_type == "Information":
            modal = InformationModal(**kwargs)
        elif modal_type == "Success":
            modal = SuccessModal(**kwargs)
        elif modal_type == "Warning":
            modal = WarningModal(**kwargs)
        elif modal_type == "Error":
            modal = ErrorModal(**kwargs)
        elif modal_type == "Custom":
            style = self.style()
            if style:
                icon = QStyle.StandardPixmap.SP_MessageBoxQuestion
                kwargs["modalIcon"] = style.standardIcon(icon).pixmap(QSize(32, 32))  # Change QSystemIcon.Warning to any desired system icon
                kwargs["description"] += "\n\nCustom modals need additional "\
                                         "styling since they are transparent "\
                                         "by default."
                modal = CustomModal(**kwargs)
        modal.show()

    def isDark(self):
        palette: QPalette = self.palette()
        background_color: QColor = palette.color(QPalette.ColorRole.Window)
        # Calculate the luminance of the background color
        luminance: float = 0.2126 * background_color.red()
        luminance += 0.7152 * background_color.green()
        luminance += 0.0722 * background_color.blue()
        # Determine if the background color is dark or light
        if luminance < 128:
            # Dark background
            return True
        else:
            # Light background
            return False


if __name__ == "__main__":
    app = QApplication([])
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    window = TestModalWindow()
    window.resize(800, 600)
    window.show()
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())