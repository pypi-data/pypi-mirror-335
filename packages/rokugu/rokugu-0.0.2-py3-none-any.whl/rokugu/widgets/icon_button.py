from pathlib import Path
from typing import Union

from PySide6.QtCore import QFileInfo, QSize
from PySide6.QtGui import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout

from rokugu.widgets.widget import Widget


class IconButton(Widget):
    def __init__(
        self, path: Union[QFileInfo, Path, str], icon_size=QSize(24, 24)
    ) -> None:
        super().__init__()

        if isinstance(path, QFileInfo):
            path = path.absoluteFilePath()
        elif isinstance(path, Path):
            path = path.as_posix()

        self.setAttribute(Qt.WidgetAttribute.WA_NoMousePropagation)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        q_v_box_layout = QVBoxLayout(self)
        q_v_box_layout.setContentsMargins(0, 0, 0, 0)
        q_v_box_layout.setSpacing(0)
        q_v_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.q_svg_widget = QSvgWidget(path)
        self.q_svg_widget.renderer().setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.q_svg_widget.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )
        self.q_svg_widget.setFixedSize(icon_size)
        q_v_box_layout.addWidget(self.q_svg_widget)

    def load(self, path: str) -> None:
        if isinstance(path, Path):
            path = path.as_posix()

        return self.q_svg_widget.load(path)

    def set_icon_size(self, q_size: QSize) -> None:
        self.q_svg_widget.setFixedSize(q_size)
