# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from typing import Optional, override

from PySide6.QtCore import QMargins, QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QWidget


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        self.clear()

    @override
    def removeWidget(self, w: QWidget) -> None:
        index = self.indexOf(w)

        if index >= 0:
            w.hide()

        super().removeWidget(w)

        p = self.parent()
        if isinstance(p, QWidget):
            p.update()
            self.parentWidget().updateGeometry()

    @override
    def removeItem(self, arg__1: QLayoutItem) -> None:
        index = self.indexOf(arg__1)

        if index >= 0:
            arg__1.widget().hide()

        super().removeItem(arg__1)

        p = self.parent()
        if isinstance(p, QWidget):
            p.update()
            self.parentWidget().updateGeometry()

    def clear(self) -> None:
        q_layout_item = self.itemAt(0)
        while q_layout_item is not None:
            self.removeItem(q_layout_item)
            q_layout_item = self.itemAt(0)

    @override
    def addItem(self, arg__1: QLayoutItem) -> None:
        self._item_list.append(arg__1)

    @override
    def count(self) -> int:
        return len(self._item_list)

    @override
    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        q_layout_item = None
        if 0 <= index < len(self._item_list):
            q_layout_item = self._item_list[index]
        return q_layout_item

    @override
    def takeAt(self, index: int) -> Optional[QLayoutItem]:
        q_layout_item = None
        if 0 <= index < len(self._item_list):
            q_layout_item = self._item_list.pop(index)
        return q_layout_item

    @override
    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    @override
    def hasHeightForWidth(self) -> bool:
        return True

    @override
    def heightForWidth(self, arg__1: int) -> int:
        height = self._do_layout(QRect(0, 0, arg__1, 0), True)
        return height

    @override
    def setGeometry(self, arg__1: QRect) -> None:
        super(FlowLayout, self).setGeometry(arg__1)
        self._do_layout(arg__1, False)

    @override
    def sizeHint(self) -> QSize:
        return self.minimumSize()

    @override
    def minimumSize(self) -> QSize:
        q_size = QSize()
        for q_layout_item in self._item_list:
            q_size = q_size.expandedTo(q_layout_item.minimumSize())
        q_size += QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )
        return q_size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal,
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Vertical,
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()
