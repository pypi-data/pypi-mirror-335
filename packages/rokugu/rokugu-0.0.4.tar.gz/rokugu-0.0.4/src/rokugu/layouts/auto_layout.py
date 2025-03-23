from enum import Enum
from math import ceil
from typing import List, Optional, Tuple, Union, override

from PySide6.QtCore import QMargins, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget


# Grid
class ResizeMode(Enum):
    FILL = "auto-fill"
    FIT = "auto-fit"


class AutoLayout(QLayout):

    def __init__(
        self,
        min_item_width: int,
        resize_mode: ResizeMode = ResizeMode.FILL,
        aspect_ratio: Optional[Union[int, float]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list: List[QLayoutItem] = []
        self._min_item_width = min_item_width  # Minimum width for items
        self._resize_mode = resize_mode
        self._aspect_ratio = aspect_ratio

    def __del__(self):
        self.clear()

    @override
    def addItem(self, arg__1: QLayoutItem) -> None:
        self._item_list.append(arg__1)
        self.invalidate()

    @override
    def count(self):
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
            self.invalidate()

        return q_layout_item

    @override
    def removeWidget(self, w: QWidget) -> None:
        q_layout_item: Optional[QLayoutItem] = None

        for _q_layout_item in self._item_list:
            q_widget = _q_layout_item.widget()

            if q_widget is not w:
                continue

            q_layout_item = _q_layout_item

            break

        if not q_layout_item:
            return

        if q_layout_item.widget():
            q_layout_item.widget().hide()
            q_layout_item.widget().deleteLater()

        self.invalidate()

        q_widget = self.parentWidget()
        if q_widget:
            q_widget.update()

    @override
    def removeItem(self, arg__1: QLayoutItem) -> None:
        try:
            self._item_list.remove(arg__1)

            if arg__1.widget():
                arg__1.widget().hide()
                arg__1.widget().deleteLater()

            self.invalidate()

            q_widget = self.parentWidget()
            if q_widget:
                q_widget.update()

        except ValueError:
            pass

    def clear(self) -> None:
        q_layout_item = self.itemAt(0)
        while q_layout_item is not None:
            self.removeItem(q_layout_item)
            q_layout_item = self.itemAt(0)

    @override
    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    @override
    def setGeometry(self, arg__1: QRect) -> None:
        super().setGeometry(arg__1)
        self._do_layout(arg__1, False)

    @override
    def sizeHint(self) -> QSize:
        return self.minimumSize()

    @override
    def hasHeightForWidth(self) -> bool:
        return True

    @override
    def heightForWidth(self, arg__1: int) -> int:
        height = self._do_layout(QRect(0, 0, arg__1, 0), True)
        return height

    @override
    def minimumSize(self) -> QSize:
        q_size = QSize()
        for q_layout_item in self._item_list:
            q_size = q_size.expandedTo(q_layout_item.minimumSize())
        q_size += QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )
        return q_size

    def _calculate_layout_params(
        self, available_width: int, spacing: int
    ) -> Tuple[int, int]:
        max_possible_items = (available_width + spacing) // (
            self._min_item_width + spacing
        )
        max_possible_items = max(1, max_possible_items)

        if self._resize_mode == ResizeMode.FIT:
            items_per_row = min(max_possible_items, len(self._item_list))
            if items_per_row == 0:
                items_per_row = 1
        else:
            items_per_row = max_possible_items
        item_width = (
            available_width - (items_per_row - 1) * spacing
        ) // items_per_row
        item_width = max(self._min_item_width, item_width)

        return items_per_row, item_width

    def _do_layout(self, rect: QRect, test_only: bool):
        margins = self.contentsMargins()
        effective_rect = rect.adjusted(
            margins.left(), margins.top(), -margins.right(), -margins.bottom()
        )

        x = effective_rect.x()
        y = effective_rect.y()
        spacing = self.spacing()
        available_width = effective_rect.width()

        items_per_row, item_width = self._calculate_layout_params(
            available_width, spacing
        )

        if self._aspect_ratio is not None:
            max_item_height = ceil(item_width / self._aspect_ratio)
        else:
            max_item_height = (
                max(item.sizeHint().height() for item in self._item_list)
                if self._item_list
                else 0
            )

        # Second pass: layout items
        if not test_only:
            current_x = x
            current_y = y
            items_in_current_row = 0

            for item in self._item_list:
                if items_in_current_row >= items_per_row:
                    current_x = x
                    current_y += max_item_height + spacing
                    items_in_current_row = 0

                item.setGeometry(
                    QRect(current_x, current_y, item_width, max_item_height)
                )
                current_x += item_width + spacing
                items_in_current_row += 1

        # Calculate total height
        rows_needed = (
            len(self._item_list) + items_per_row - 1
        ) // items_per_row
        total_height = y
        if len(self._item_list) > 0:
            total_height += (rows_needed - 1) * (
                max_item_height + spacing
            ) + max_item_height

        margin_y = (
            self.contentsMargins().top() + self.contentsMargins().bottom()
        )
        return (total_height - effective_rect.y()) + margin_y
