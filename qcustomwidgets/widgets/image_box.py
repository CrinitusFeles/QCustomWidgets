from pathlib import Path
from typing_extensions import override
from loguru import logger
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtGui import QPixmap, QMovie, QImage, QIcon, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer


SOURCE = str | Path | QPixmap | QMovie | QImage | QIcon
T_FAST = Qt.TransformationMode.FastTransformation
T_SMOOTH = Qt.TransformationMode.SmoothTransformation
AR_NONE = Qt.AspectRatioMode.IgnoreAspectRatio
AR_KEEP = Qt.AspectRatioMode.KeepAspectRatio


def svg_to_pixmap(svg_filename: str, width: int, height: int,
                  color: str) -> QPixmap:
    renderer = QSvgRenderer(svg_filename)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter) # this is the destination, and only its alpha is used!
    painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return pixmap


class ImageBox(QLabel):
    def __init__(self, source: SOURCE | None = None,
                 parent: QWidget | None = None,
                 keepAspectRatio=True,
                 smoothScale=True,
                 color: str = '') -> None:
        super().__init__(parent)

        self.source: SOURCE | None = source
        self.animated = False
        self.is_svg = False

        self.keepAspectRatio: bool = keepAspectRatio
        self.smoothScale: bool = smoothScale
        self.origin_pixmap: QPixmap | None = None
        self._movie: QMovie | None = None
        if isinstance(self.source, Path):
            self.source = str(self.source)

        if self.source is not None:
            self.set_source(self.source)
        if color:
            self.change_svg_color(color)

    def set_source(self, source: SOURCE):
        self.source = source
        self.animated = False

        if isinstance(self.source, Path):
            self.source = str(self.source)

        if isinstance(self.source, str):
            if not self.source.startswith((':/', ':svg/', ':png/', ':ico/')) and \
                not Path(self.source).exists():
                logger.warning(f'Pixmap path error: {self.source} not exists')
            if self.source.endswith(".gif"):
                self.animated = True
                self._movie = QMovie(self.source)
            else:
                self.origin_pixmap = QPixmap(self.source)
        elif isinstance(self.source, QIcon):
            self.origin_pixmap = self.source.pixmap(self.size())
        elif isinstance(self.source, QPixmap):
            self.origin_pixmap = QPixmap(self.source)
        elif isinstance(self.source, QImage):
            self.origin_pixmap = QPixmap.fromImage(self.source)
        elif isinstance(self.source, QMovie):
            self.animated = True
            self._movie = QMovie(self.source)
        else:
            raise TypeError(f"Argument 1 has unexpected type '{type(self.source)}'")

        if isinstance(self.source, QMovie):
            if self._movie:
                self.setMovie(self._movie)
                self._movie.start()
        elif self.origin_pixmap:
            self.setPixmap(self.origin_pixmap)
        self.resizeEvent(None)

    @override
    def resizeEvent(self, a0):
        w, h = self.width(), self.height()
        tr: Qt.TransformationMode = (T_FAST, T_SMOOTH)[self.smoothScale]
        ar: Qt.AspectRatioMode = (AR_NONE, AR_KEEP)[self.keepAspectRatio]
        if self.animated and self._movie:
            self._movie.setScaledSize(QSize(w, h))
        elif self.origin_pixmap:
            pixmap: QPixmap = self.origin_pixmap.scaled(w, h, transformMode=tr,
                                                        aspectRatioMode=ar)
            self.setPixmap(pixmap)

    def change_svg_color(self, new_color: str):
        if self.origin_pixmap and isinstance(self.source, str):
            self.origin_pixmap = svg_to_pixmap(self.source, self.origin_pixmap.width(),
                                               self.origin_pixmap.height(), new_color)
            self.resizeEvent(None)
