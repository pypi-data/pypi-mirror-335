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

        self._aspect_ratio_mode = Qt.AspectRatioMode.KeepAspectRatio
        self.setAttribute(Qt.WidgetAttribute.WA_NoMousePropagation)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        q_v_box_layout = QVBoxLayout(self)
        q_v_box_layout.setContentsMargins(0, 0, 0, 0)
        q_v_box_layout.setSpacing(0)
        q_v_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._q_svg_widget = QSvgWidget(path)
        self._q_svg_widget.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self._q_svg_widget.setFixedSize(icon_size)
        self._q_svg_renderer = self._q_svg_widget.renderer()
        self._q_svg_renderer.setAspectRatioMode(self._aspect_ratio_mode)
        q_v_box_layout.addWidget(self._q_svg_widget)

    def load(self, path: Union[str, Path]) -> bool:
        if isinstance(path, Path):
            path = path.as_posix()

        _ = self._q_svg_renderer.load(path)
        self._q_svg_renderer.setAspectRatioMode(self._aspect_ratio_mode)
        return _

    def icon_size(self) -> QSize:
        return self._q_svg_widget.size()

    def set_icon_size(self, q_size: QSize) -> None:
        self._q_svg_widget.setFixedSize(q_size)

    def aspect_ratio_mode(self) -> Qt.AspectRatioMode:
        return self._q_svg_renderer.aspectRatioMode()

    def set_aspect_ratio_mode(self, mode: Qt.AspectRatioMode) -> None:
        self._q_svg_renderer.setAspectRatioMode(mode)
        self._aspect_ratio_mode = mode
