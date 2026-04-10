from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit,
    QPushButton, QCheckBox, QScrollArea, QWidget, QMessageBox,
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from datetime import date, time

from app.core.models import Task, RecurrenceRule
from app.ui.main_window.recurrence_picker import RecurrencePicker


class TaskForm(QDialog):
    """Görev ekleme ve düzenleme diyalogu."""

    def __init__(self, parent=None, task: Task | None = None, show_recurrence: bool = True):
        super().__init__(parent)
        self._task = task
        self._show_recurrence = show_recurrence
        self.setWindowTitle("Görev Düzenle" if task else "Yeni Görev")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()
        if task:
            self._populate(task)

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        # Başlık
        root.addWidget(self._label("Başlık *"))
        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText("Görev başlığını girin...")
        self.edit_title.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        root.addWidget(self.edit_title)

        # Açıklama
        root.addWidget(self._label("Açıklama"))
        self.edit_desc = QTextEdit()
        self.edit_desc.setPlaceholderText("Opsiyonel açıklama...")
        self.edit_desc.setFixedHeight(80)
        self.edit_desc.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        root.addWidget(self.edit_desc)

        # Tarih
        date_row = QHBoxLayout()
        date_col = QVBoxLayout()
        date_col.addWidget(self._label("Tarih *"))
        self.edit_date = QDateEdit()
        self.edit_date.setCalendarPopup(True)
        self.edit_date.setDate(QDate.currentDate())
        self.edit_date.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        date_col.addWidget(self.edit_date)
        date_row.addLayout(date_col)

        # Saat (opsiyonel) — checkbox işaretlenince görünür
        time_col = QVBoxLayout()
        self.chk_time = QCheckBox("Saat ekle")
        self.edit_time = QTimeEdit()
        self.edit_time.setDisplayFormat("HH:mm")
        self.edit_time.setTime(QTime.currentTime())
        self.edit_time.setVisible(False)
        self.edit_time.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.chk_time.toggled.connect(self.edit_time.setVisible)
        time_col.addWidget(self.chk_time)
        time_col.addWidget(self.edit_time)
        date_row.addLayout(time_col)
        root.addLayout(date_row)

        # Tekrarlama (instance düzenlemede gizlenir)
        self.recurrence_picker = RecurrencePicker()
        self.recurrence_picker.setVisible(self._show_recurrence)
        root.addWidget(self.recurrence_picker)

        # Butonlar
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("İptal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("section_label")
        return lbl

    # ------------------------------------------------------------------
    def _populate(self, task: Task):
        self.edit_title.setText(task.title)
        self.edit_desc.setPlainText(task.description or "")
        self.edit_date.setDate(QDate(task.due_date.year, task.due_date.month, task.due_date.day))
        if task.due_time:
            self.chk_time.setChecked(True)
            self.edit_time.setVisible(True)
            self.edit_time.setTime(QTime(task.due_time.hour, task.due_time.minute))
        if task.recurrence_rule:
            self.recurrence_picker.set_rule(task.recurrence_rule)

    # ------------------------------------------------------------------
    def _on_save(self):
        title = self.edit_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Hata", "Başlık boş olamaz.")
            self.edit_title.setFocus()
            return

        qd = self.edit_date.date()
        self._result_date = date(qd.year(), qd.month(), qd.day())
        self._result_time = None
        if self.chk_time.isChecked():
            qt = self.edit_time.time()
            self._result_time = time(qt.hour(), qt.minute())

        self._result_title = title
        self._result_desc  = self.edit_desc.toPlainText().strip() or None
        self._result_rule  = self.recurrence_picker.get_rule()
        self.accept()

    # ------------------------------------------------------------------
    def get_data(self) -> dict:
        """accept() sonrası form verilerini döner."""
        return {
            "title":       self._result_title,
            "description": self._result_desc,
            "due_date":    self._result_date,
            "due_time":    self._result_time,
            "recurrence_rule": self._result_rule,
        }
