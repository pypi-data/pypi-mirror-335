from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtWidgets import QApplication, QFrame
from typing_extensions import override


# NOTICE: dont use yet
class Popup(QFrame):
    def __init__(self, p):
        super().__init__(p)

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )
        self.setFixedSize(256, 256)

    @override
    def show(self, q_point: QPoint = QCursor.pos(), /) -> None:
        """
        Examples:

        ```py
        q_widget = QWidget()
        q_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # 1
        q_widget.customContextMenuRequested.connect(x.show)

        # 2
        q_widget.customContextMenuRequested.connect(lambda _:x.show())

        # 3
        def _():
            q_rect = q_widget.rect()
            q_point = q_widget.mapToGlobal(QPoint(q_rect.width(),q_rect.height()))
            x.show(q_pont)
        q_widget.pressed.connect(_)
        ```
        """

        q_screen = QApplication.screenAt(q_point)
        if q_screen:
            q_rect = q_screen.geometry()
        else:
            q_rect = QRect(
                0,
                0,
                QApplication.primaryScreen().size().width(),
                QApplication.primaryScreen().size().height(),
            )

        q_size = self.sizeHint()
        x = q_point.x()
        y = q_point.y()

        if x + q_size.width() > q_rect.x() + q_rect.width():
            x = q_rect.x() + q_rect.width() - q_size.width()

        if y + q_size.height() > q_rect.y() + q_rect.height():
            x = q_rect.y() + q_rect.height() - q_size.height()

        self.move(x, y)

        return super().show()

    def showEvent(self, event, /):
        q_application = QApplication.instance()

        if q_application:
            q_application.installEventFilter(self)
        super().showEvent(event)

    def hideEvent(self, event, /):
        q_application = QApplication.instance()

        if q_application:
            q_application.removeEventFilter(self)
        super().hideEvent(event)

    def eventFilter(self, watched, event: QEvent, /):
        if not isinstance(event, QMouseEvent):
            return super().eventFilter(watched, event)

        if event.type() is not QEvent.Type.MouseButtonPress:
            return super().eventFilter(watched, event)

        if self.geometry().contains(event.globalPos()):
            return super().eventFilter(watched, event)

        self.hide()
        return True
