from pathlib import Path
from typing import Literal, Union, override

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QPaintEvent, QPixmap
from PySide6.QtWidgets import QWidget


class ImageBackground(QWidget):
    def __init__(
        self,
        path: Union[Path, str],
        object_fit: Literal[
            "contain", "cover", "fill", "none", "scale-down"
        ] = "cover",
    ) -> None:
        super().__init__()

        if isinstance(path, Path):
            path = path.as_posix()

        self.q_pixmap = QPixmap(path)
        self.object_fit = object_fit

    def load(self, path: Union[Path, str]) -> None:
        if isinstance(path, Path):
            path = path.as_posix()

        self.q_pixmap.load(path)

    @override
    def paintEvent(self, event: QPaintEvent) -> None:
        q_painter = QPainter(self)
        q_rect = self.rect()

        img_rect = self.q_pixmap.rect()

        if self.object_fit == "scale-down":
            img_aspect = img_rect.width() / img_rect.height()
            widget_aspect = q_rect.width() / q_rect.height()

            scaled_width = img_rect.width()
            scaled_height = img_rect.height()

            if (
                img_rect.width() > q_rect.width()
                or img_rect.height() > q_rect.height()
            ):
                if img_aspect > widget_aspect:
                    # Image is wider than widget
                    scaled_width = q_rect.width()
                    scaled_height = int(scaled_width / img_aspect)
                else:
                    # Image is taller than widget
                    scaled_height = q_rect.height()
                    scaled_width = int(scaled_height * img_aspect)

            q_painter.drawPixmap(
                QRect(0, 0, scaled_width, scaled_height), self.q_pixmap
            )

        elif self.object_fit == "contain":
            img_aspect = img_rect.width() / img_rect.height()
            widget_aspect = q_rect.width() / q_rect.height()

            if img_aspect > widget_aspect:
                scaled_width = q_rect.width()
                scaled_height = int(scaled_width / img_aspect)
            else:
                scaled_height = q_rect.height()
                scaled_width = int(scaled_height * img_aspect)

            x = int((q_rect.width() - scaled_width) / 2)
            y = int((q_rect.height() - scaled_height) / 2)
            q_painter.drawPixmap(
                QRect(x, y, scaled_width, scaled_height), self.q_pixmap
            )

        elif self.object_fit == "cover":
            img_aspect = img_rect.width() / img_rect.height()
            widget_aspect = q_rect.width() / q_rect.height()

            if img_aspect > widget_aspect:
                scaled_height = q_rect.height()
                scaled_width = int(scaled_height * img_aspect)
            else:
                scaled_width = q_rect.width()
                scaled_height = int(scaled_width / img_aspect)

            x = int((q_rect.width() - scaled_width) / 2)
            y = int((q_rect.height() - scaled_height) / 2)
            q_painter.drawPixmap(
                QRect(x, y, scaled_width, scaled_height), self.q_pixmap
            )

        elif self.object_fit == "fill":
            q_painter.drawPixmap(
                QRect(0, 0, q_rect.width(), q_rect.height()), self.q_pixmap
            )

        else:
            q_painter.drawPixmap(0, 0, self.q_pixmap)

        return super().paintEvent(event)
