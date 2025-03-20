import weakref
from typing import Any, Dict, Optional, overload, override

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QPainter, QPaintEvent, QShowEvent
from PySide6.QtWidgets import QStackedLayout, QStyle, QStyleOption, QWidget


class Router(QWidget):
    current_changed = Signal(int, str)
    widget_added = Signal(int, str)
    widget_removed = Signal(int, str)

    def __init__(self, default: Optional[str] = None) -> None:
        super().__init__()

        self.q_shortcutional[str] = default

        self._name_to_q_widget: Dict[str, weakref.ref[QWidget]] = dict()
        self._id_to_name: Dict[int, str] = dict()
        self._index_to_name: Dict[int, str] = dict()

        self.q_stacked_layout = QStackedLayout(self)
        self.q_stacked_layout.currentChanged.connect(self._current_changed)
        self.q_stacked_layout.widgetRemoved.connect(self._widget_removed)

    def add(self, name: str, q_widget: QWidget) -> int:
        if len(name) == 0:
            raise ValueError(f"QWidget with name '{name}' can not be empty")

        if name in self._name_to_q_widget:
            raise ValueError(f"QWidget with name '{name}' already exists")

        index = self.q_stacked_layout.addWidget(q_widget)

        self._name_to_q_widget[name] = weakref.ref(q_widget)
        self._id_to_name[id(q_widget)] = name
        self._index_to_name[index] = name

        self.widget_added.emit(index, name)

        return index

    def insert(self, index: int, name: str, q_widget: QWidget) -> int:
        if len(name) == 0:
            raise ValueError(f"QWidget with name '{name}' can not be empty")

        if name in self._name_to_q_widget:
            raise ValueError(f"QWidget with name '{name}' already exists")

        index = self.q_stacked_layout.insertWidget(index, q_widget)

        self._name_to_q_widget[name] = weakref.ref(q_widget)
        self._id_to_name[id(q_widget)] = name

        _index_to_name = dict()
        for k, v in self._name_to_q_widget.items():
            _q_widget = v()

            if _q_widget is None:
                continue

            _index = self.q_stacked_layout.indexOf(_q_widget)

            if _index == -1:
                continue

            _index_to_name[_index] = k

        self._index_to_name = _index_to_name

        self.widget_added.emit(index, name)

        return index

    @overload
    def remove(self, arg__1: QWidget) -> None:
        pass

    @overload
    def remove(self, arg__1: int) -> None:
        pass

    @overload
    def remove(self, arg__1: str) -> None:
        pass

    def remove(self, arg__1: Any) -> None:
        if isinstance(arg__1, QWidget):
            self.q_stacked_layout.removeWidget(arg__1)

        elif isinstance(arg__1, int):
            q_widget = self.q_stacked_layout.widget(arg__1)

            if q_widget is None:
                return

            return self.q_stacked_layout.removeWidget(q_widget)

        elif isinstance(arg__1, str):
            wr = self._name_to_q_widget.get(arg__1, None)

            if wr is None:
                return

            q_widget = wr()

            if q_widget is None:
                return

            return self.q_stacked_layout.removeWidget(q_widget)

        raise TypeError()

    @overload
    def to_route(self, arg__1: QWidget) -> None:
        pass

    @overload
    def to_route(self, arg__1: int) -> None:
        pass

    @overload
    def to_route(self, arg__1: str) -> None:
        pass

    def to_route(self, arg__1: Any) -> None:
        if isinstance(arg__1, QWidget):
            return self.q_stacked_layout.setCurrentWidget(arg__1)

        elif isinstance(arg__1, int):
            return self.q_stacked_layout.setCurrentIndex(arg__1)

        elif isinstance(arg__1, str):
            wr = self._name_to_q_widget.get(arg__1, None)

            if wr is None:
                return

            q_widget = wr()

            if q_widget is None:
                return

            return self.q_stacked_layout.setCurrentWidget(q_widget)
        raise TypeError()

    def first(self) -> None:
        if (self.q_stacked_layout.count() > 0) and (
            self.q_stacked_layout.currentIndex() != 0
        ):
            self.q_stacked_layout.setCurrentIndex(0)

    def prev(self) -> None:
        index = self.q_stacked_layout.currentIndex()
        count = self.q_stacked_layout.count()

        if index > 0 and index < count:
            self.q_stacked_layout.setCurrentIndex((index - 1))

    def next(self) -> None:
        index = self.q_stacked_layout.currentIndex()
        count = self.q_stacked_layout.count()

        if index > -1 and index < (count - 1):
            self.q_stacked_layout.setCurrentIndex((index + 1))

    def last(self) -> None:
        count = self.q_stacked_layout.count()

        if count > 0:
            self.q_stacked_layout.setCurrentIndex((count - 1))

    def currentWidget(self) -> Optional[QWidget]:
        return self.q_stacked_layout.currentWidget()

    def currentIndex(self) -> int:
        return self.q_stacked_layout.currentIndex()

    def currentName(self) -> Optional[str]:
        q_widget = self.q_stacked_layout.currentWidget()

        if q_widget is None:
            return

        return self._id_to_name.get(id(q_widget), None)

    @overload
    def contains(self, arg__1: QWidget) -> bool:
        pass

    @overload
    def contains(self, arg__1: int) -> bool:
        pass

    @overload
    def contains(self, arg__1: str) -> bool:
        pass

    def contains(self, arg__1: Any) -> bool:
        if isinstance(arg__1, QWidget):
            return self.q_stacked_layout.indexOf(arg__1) != -1

        elif isinstance(arg__1, int):
            return bool(self.q_stacked_layout.widget(arg__1))

        elif isinstance(arg__1, str):
            wr = self._name_to_q_widget.get(arg__1, None)

            if wr is None:
                return False

            q_widget = wr()

            if q_widget is None:
                return False

            return self.q_stacked_layout.indexOf(q_widget) != -1

        raise TypeError()

    @overload
    def widget(self, arg__1: int) -> Optional[QWidget]:
        pass

    @overload
    def widget(self, arg__1: str) -> Optional[QWidget]:
        pass

    def widget(self, arg__1: Any) -> Optional[QWidget]:
        if isinstance(arg__1, int):
            return self.q_stacked_layout.widget(arg__1)

        elif isinstance(arg__1, str):
            wr = self._name_to_q_widget.get(arg__1, None)

            if wr is None:
                return

            q_widget = wr()

            if q_widget is None:
                return

            index = self.q_stacked_layout.indexOf(q_widget)

            if index == -1:
                return

            return self.q_stacked_layout.widget(index)

        raise TypeError()

    @overload
    def index(self, arg__1: QWidget) -> int:
        pass

    @overload
    def index(self, arg__1: str) -> int:
        pass

    def index(self, arg__1: Any) -> int:
        if isinstance(arg__1, QWidget):
            return self.q_stacked_layout.indexOf(arg__1)

        elif isinstance(arg__1, str):
            wr = self._name_to_q_widget.get(arg__1, None)

            if wr is None:
                return -1

            q_widget = wr()

            if q_widget is None:
                return -1

            return self.q_stacked_layout.indexOf(q_widget)

        raise TypeError()

    @overload
    def name(self, arg__1: QWidget) -> Optional[str]:
        pass

    @overload
    def name(self, arg__1: int) -> Optional[str]:
        pass

    def name(self, arg__1: Any) -> Optional[str]:
        if isinstance(arg__1, QWidget):
            return self._id_to_name.get(id(arg__1), None)

        elif isinstance(arg__1, int):
            q_widget = self.q_stacked_layout.widget(arg__1)

            if q_widget is None:
                return

            return self._id_to_name.get(id(q_widget), None)

        raise TypeError()

    def count(self) -> int:
        return self.q_stacked_layout.count()

    @Slot(int)
    def _current_changed(self, index: int) -> None:
        name = self._index_to_name.get(index, None)

        if name is None:
            return

        self.current_changed.emit(index, name)

    @Slot(int)
    def _widget_removed(self, index: int) -> None:
        name = self._index_to_name.get(index, None)

        if name is None:
            return

        wr = self._name_to_q_widget.get(name, None)

        if wr is None:
            return

        q_widget = wr()

        if q_widget is None:
            return

        del self._id_to_name[id(q_widget)]
        del self._name_to_q_widget[name]

        _index_to_name = dict()
        for k, v in self._name_to_q_widget.items():
            _q_widget = v()

            if _q_widget is None:
                continue

            _index = self.q_stacked_layout.indexOf(_q_widget)

            if _index == -1:
                continue

            _index_to_name[_index] = k

        self._index_to_name = _index_to_name

        self.widget_removed.emit(index, name)

    @override
    def paintEvent(self, event: QPaintEvent) -> None:
        q_style_option = QStyleOption()
        q_style_option.initFrom(self)

        q_painter = QPainter(self)

        self.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_Widget, q_style_option, q_painter, self
        )

    @override
    def showEvent(self, event: QShowEvent) -> None:
        if isinstance(self.default, str):
            self.to_route(self.default)

        return super().showEvent(event)
