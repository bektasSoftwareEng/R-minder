from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from app.core.models import Task
from app.ui.styles.colors import PRIORITY_COLORS, BG_SECONDARY, TEXT_MUTED


class TaskCard(QFrame):
    complete_requested = pyqtSignal(int)
    edit_requested     = pyqtSignal(int)
    delete_requested   = pyqtSignal(int)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("task_card")
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Öncelik renk çubuğu (sol kenar)
        color_bar = QFrame()
        color_bar.setFixedWidth(4)
        color_bar.setFixedHeight(40)
        color_bar.setStyleSheet(
            f"background-color: {PRIORITY_COLORS.get(self.task.priority, '#CDD6F4')};"
            "border-radius: 2px;"
        )
        layout.addWidget(color_bar)

        # İçerik
        content = QVBoxLayout()
        content.setSpacing(2)

        title_text = self.task.title
        if self.task.is_completed:
            title_text = f"<s>{title_text}</s>"

        self.lbl_title = QLabel(title_text)
        self.lbl_title.setObjectName("title_label")
        self.lbl_title.setWordWrap(True)
        content.addWidget(self.lbl_title)

        # Tarih / saat satırı
        date_str = self.task.due_date.strftime("%d %b %Y")
        if self.task.due_time:
            date_str += f"  {self.task.due_time.strftime('%H:%M')}"
        lbl_date = QLabel(date_str)
        lbl_date.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        content.addWidget(lbl_date)

        layout.addLayout(content)
        layout.addStretch()

        # Eylem butonları
        if not self.task.is_completed:
            btn_done = QPushButton("✓")
            btn_done.setObjectName("btn_icon")
            btn_done.setToolTip("Tamamlandı olarak işaretle")
            btn_done.setFixedSize(30, 30)
            btn_done.clicked.connect(lambda: self.complete_requested.emit(self.task.id))
            layout.addWidget(btn_done)

        btn_edit = QPushButton("✎")
        btn_edit.setObjectName("btn_icon")
        btn_edit.setToolTip("Düzenle")
        btn_edit.setFixedSize(30, 30)
        btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.task.id))
        layout.addWidget(btn_edit)

        btn_del = QPushButton("✕")
        btn_del.setObjectName("btn_danger")
        btn_del.setToolTip("Sil")
        btn_del.setFixedSize(30, 30)
        btn_del.clicked.connect(lambda: self.delete_requested.emit(self.task.id))
        layout.addWidget(btn_del)


class TaskListWidget(QWidget):
    """Görevleri liste halinde gösteren, kaydırılabilir alan."""
    complete_requested = pyqtSignal(int)
    edit_requested     = pyqtSignal(int)
    delete_requested   = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._container = QWidget()
        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll)

        self._empty_label = QLabel("Görev yok")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; padding: 40px;")
        root.addWidget(self._empty_label)
        self._empty_label.hide()

    def load_tasks(self, tasks: list[Task]):
        # Mevcut kartları temizle (stretch hariç)
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not tasks:
            self._scroll.hide()
            self._empty_label.show()
            return

        self._empty_label.hide()
        self._scroll.show()

        for task in tasks:
            card = TaskCard(task)
            card.complete_requested.connect(self.complete_requested)
            card.edit_requested.connect(self.edit_requested)
            card.delete_requested.connect(self.delete_requested)
            self._list_layout.insertWidget(self._list_layout.count() - 1, card)
