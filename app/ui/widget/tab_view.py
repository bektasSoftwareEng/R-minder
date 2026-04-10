from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.core.models import Task
from app.ui.widget.task_card import WidgetTaskCard
from app.ui.styles.colors import TEXT_MUTED


class WidgetTabView(QWidget):
    """Widget içindeki tek sekme — kaydırılabilir kompakt görev listesi."""

    complete_requested = pyqtSignal(object)
    delete_requested   = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll)

        self._empty = QLabel("Görev yok")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; padding: 20px;")
        root.addWidget(self._empty)
        self._empty.hide()

    def load_tasks(self, tasks: list[Task]):
        # Önceki kartları temizle
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not tasks:
            self._scroll.hide()
            self._empty.show()
            return

        self._empty.hide()
        self._scroll.show()

        for task in tasks:
            card = WidgetTaskCard(task)
            card.complete_requested.connect(self.complete_requested)
            card.delete_requested.connect(self.delete_requested)
            self._list_layout.insertWidget(self._list_layout.count() - 1, card)
