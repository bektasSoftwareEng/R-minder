from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from app.core.models import Task
from app.ui.styles.colors import PRIORITY_COLORS, TEXT_MUTED, BG_SECONDARY


class WidgetTaskCard(QFrame):
    """Widget için kompakt görev kartı."""

    complete_requested = pyqtSignal(object)
    delete_requested   = pyqtSignal(object)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("task_card")
        self.setFixedHeight(54)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Öncelik renk çubuğu
        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setStyleSheet(
            f"background-color: {PRIORITY_COLORS.get(self.task.priority, '#CDD6F4')};"
            "border-radius: 2px;"
        )
        layout.addWidget(bar)

        # İçerik
        content = QVBoxLayout()
        content.setSpacing(1)
        content.setContentsMargins(0, 0, 0, 0)

        # Başlık — uzunsa kırp
        title = self.task.title
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        lbl_title.setStyleSheet("color: #CDD6F4;")
        lbl_title.setMaximumWidth(170)
        # Elide (...)  için tooltip
        lbl_title.setToolTip(title)
        lbl_title.setText(self._elide(title, 22))
        content.addWidget(lbl_title)

        # Tarih / saat
        date_str = self.task.due_date.strftime("%d %b")
        if self.task.due_time:
            date_str += f"  {self.task.due_time.strftime('%H:%M')}"
        lbl_date = QLabel(date_str)
        lbl_date.setFont(QFont("Segoe UI", 9))
        lbl_date.setStyleSheet(f"color: {TEXT_MUTED};")
        content.addWidget(lbl_date)

        layout.addLayout(content)
        layout.addStretch()

        # Butonlar
        if not self.task.is_completed:
            btn_done = QPushButton("✓")
            btn_done.setObjectName("btn_icon")
            btn_done.setFixedSize(24, 24)
            btn_done.setToolTip("Tamamlandı")
            btn_done.clicked.connect(lambda: self.complete_requested.emit(self.task))
            layout.addWidget(btn_done)

        btn_del = QPushButton("✕")
        btn_del.setObjectName("btn_icon")
        btn_del.setFixedSize(24, 24)
        btn_del.setToolTip("Sil")
        btn_del.setStyleSheet("color: #F38BA8;")
        btn_del.clicked.connect(lambda: self.delete_requested.emit(self.task))
        layout.addWidget(btn_del)

    @staticmethod
    def _elide(text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[:max_chars - 1] + "…"
