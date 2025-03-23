from typing import Any, overload

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem


class ListWidget(QListWidget):
    changed = Signal(QListWidgetItem)

    def __init__(self) -> None:
        super().__init__()

        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setUniformItemSizes(False)
        self.setTabKeyNavigation(True)

        self.itemActivated.connect(
            lambda q_list_widget_item: self.changed.emit(q_list_widget_item)
        )
        self.itemPressed.connect(
            lambda q_list_widget_item: self.changed.emit(q_list_widget_item)
        )

    @overload
    def remove(self, arg__1: int) -> bool:
        pass

    @overload
    def remove(self, arg__1: QListWidgetItem) -> bool:
        pass

    def remove(self, arg__1) -> bool:
        if isinstance(arg__1, int):
            return self.model().removeRow(arg__1)
        elif isinstance(arg__1, QListWidgetItem):
            index = self.row(arg__1)

            if index == -1:
                return False

            return self.model().removeRow(index)

        raise TypeError()

    @overload
    def select(self, arg__1: int) -> None:
        pass

    @overload
    def select(self, arg__1: QListWidgetItem) -> None:
        pass

    def select(self, arg__1: Any) -> None:
        if isinstance(arg__1, int):
            q_list_widget_item = self.item(arg__1)

            if not isinstance(q_list_widget_item, QListWidgetItem):
                return

            self.clearSelection()

            q_list_widget_item.setSelected(True)

            self.scrollToItem(
                q_list_widget_item, QListWidget.ScrollHint.EnsureVisible
            )
            self.changed.emit(q_list_widget_item)
            return
        elif isinstance(arg__1, QListWidgetItem):
            index = self.row(arg__1)

            if index == -1:
                return

            self.clearSelection()

            arg__1.setSelected(True)

            self.scrollToItem(arg__1, QListWidget.ScrollHint.EnsureVisible)
            self.changed.emit(arg__1)
            return

        raise TypeError()
