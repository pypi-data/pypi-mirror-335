from PySide6.QtGui import QKeySequence, QShortcut, Qt
from PySide6.QtWidgets import QApplication, QMainWindow


class Window(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        q_shortcut = QShortcut(
            QKeySequence(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_Q),
            self,
        )
        q_shortcut.activated.connect(QApplication.quit)
