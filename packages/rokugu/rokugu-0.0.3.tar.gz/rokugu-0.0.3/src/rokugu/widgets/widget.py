from typing import override

from PySide6.QtCore import QEvent, QTimer, Signal
from PySide6.QtGui import (
    QEnterEvent,
    QFocusEvent,
    QHideEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QShowEvent,
    Qt,
)
from PySide6.QtWidgets import QStyle, QStyleOption, QWidget


class Widget(QWidget):
    shown = Signal()
    hidden = Signal()

    enabled = Signal()
    disabled = Signal()

    focused_in = Signal()
    focused_out = Signal()

    hovered_in = Signal(QEnterEvent)
    hovered_out = Signal(QEvent)
    pressed_in = Signal(QMouseEvent)
    pressed_out = Signal(QMouseEvent)
    long_pressed = Signal()
    clicked = Signal()
    double_clicked = Signal(QMouseEvent)

    def __init__(self) -> None:
        super().__init__()

        self.q_timer = QTimer(self)
        self.q_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.q_timer.setSingleShot(True)
        self.q_timer.setInterval(500)
        self.q_timer.timeout.connect(self.long_pressed.emit)

    @override
    def paintEvent(self, event: QPaintEvent) -> None:
        q_style_option = QStyleOption()
        q_style_option.initFrom(self)

        q_painter = QPainter(self)

        self.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_Widget, q_style_option, q_painter, self
        )

    @override
    def showEvent(self, event: QShowEvent, /) -> None:
        self.shown.emit()
        return super().showEvent(event)

    @override
    def hideEvent(self, event: QHideEvent, /) -> None:
        self.hidden.emit()
        return super().hideEvent(event)

    @override
    def setEnabled(self, arg__1: bool) -> None:
        _ = self.isEnabled()

        super().setEnabled(arg__1)

        if _ is self.isEnabled():
            return

        if arg__1:
            self.enabled.emit()
        else:
            self.disabled.emit()

    @override
    def setDisabled(self, arg__1: bool) -> None:
        _ = self.isEnabled()

        super().setDisabled(arg__1)

        if _ is self.isEnabled():
            return

        if arg__1:
            self.disabled.emit()
        else:
            self.enabled.emit()

    @override
    def enterEvent(self, event: QEnterEvent) -> None:
        self.hovered_in.emit(event)
        return super().enterEvent(event)

    @override
    def leaveEvent(self, event: QEvent) -> None:
        self.hovered_out.emit(event)

        if self.q_timer.isActive():
            self.q_timer.stop()

        return super().leaveEvent(event)

    @override
    def focusInEvent(self, arg__1: QFocusEvent, /) -> None:
        self.focused_in.emit()
        return super().focusInEvent(arg__1)

    @override
    def focusOutEvent(self, arg__1: QFocusEvent, /) -> None:
        self.focused_out.emit()
        return super().focusOutEvent(arg__1)

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.pressed_in.emit(event)

        self.q_timer.start()

        return super().mousePressEvent(event)

    @override
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.pressed_out.emit(event)

        if self.q_timer.isActive():
            self.q_timer.stop()

        if self.rect().contains(event.pos()):
            self.clicked.emit()

        return super().mouseReleaseEvent(event)

    @override
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.double_clicked.emit(event)
        return super().mouseDoubleClickEvent(event)
