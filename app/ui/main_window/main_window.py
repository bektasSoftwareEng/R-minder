from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer

from app.services import task_service
from app.core import repository
from app.ui.main_window.task_list import TaskListWidget
from app.ui.main_window.task_form import TaskForm


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("R-minder")
        self.setMinimumSize(560, 600)
        self._build_ui()
        self.refresh()

        # Her 60 saniyede bir otomatik yenile (öncelik renkleri için)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(60_000)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start()

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Üst bar
        header = QWidget()
        header.setObjectName("header_bar")
        header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)

        lbl_app = QLabel("R-minder")
        lbl_app.setStyleSheet("font-size: 18px; font-weight: 700; color: #89B4FA;")
        h_layout.addWidget(lbl_app)
        h_layout.addStretch()

        btn_add = QPushButton("+ Yeni Görev")
        btn_add.clicked.connect(self.open_add_form)
        h_layout.addWidget(btn_add)
        root.addWidget(header)

        # Sekmeler
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.list_all      = TaskListWidget()
        self.list_today    = TaskListWidget()
        self.list_tomorrow = TaskListWidget()
        self.list_week     = TaskListWidget()

        self.tabs.addTab(self.list_today,    "Bugün")
        self.tabs.addTab(self.list_tomorrow, "Yarın")
        self.tabs.addTab(self.list_week,     "Bu Hafta")
        self.tabs.addTab(self.list_all,      "Tümü")

        for lst in (self.list_all, self.list_today, self.list_tomorrow, self.list_week):
            lst.complete_requested.connect(self._on_complete)
            lst.edit_requested.connect(self._on_edit)
            lst.delete_requested.connect(self._on_delete)

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.addWidget(self.tabs)
        root.addWidget(content)

    # ------------------------------------------------------------------
    def refresh(self):
        self.list_today.load_tasks(task_service.get_tasks_for_today())
        self.list_tomorrow.load_tasks(task_service.get_tasks_for_tomorrow())
        self.list_week.load_tasks(task_service.get_tasks_for_this_week())
        self.list_all.load_tasks(task_service.get_all_tasks())

        # Sekme başlıklarını güncelle
        today_count = len(task_service.get_tasks_for_today())
        if today_count:
            self.tabs.setTabText(0, f"Bugün ({today_count})")
        else:
            self.tabs.setTabText(0, "Bugün")

    # ------------------------------------------------------------------
    def open_add_form(self, task=None):
        form = TaskForm(self, task)
        if form.exec():
            data = form.get_data()
            if task:
                task.title       = data["title"]
                task.description = data["description"]
                task.due_date    = data["due_date"]
                task.due_time    = data["due_time"]
                task_service.update_task(task)
            else:
                task_service.create_task(
                    title=data["title"],
                    due_date=data["due_date"],
                    description=data["description"] or "",
                    due_time=data["due_time"],
                    recurrence_rule=data["recurrence_rule"],
                )
            self.refresh()

    def _on_complete(self, task_id: int):
        task_service.complete_task(task_id)
        self.refresh()

    def _on_edit(self, task_id: int):
        task = repository.get_task(task_id)
        if task and task.recurrence_id:
            task.recurrence_rule = repository.get_recurrence_rule(task.recurrence_id)
        self.open_add_form(task)

    def _on_delete(self, task_id: int):
        task = repository.get_task(task_id)
        if task is None:
            return

        if task.recurrence_id:
            reply = QMessageBox.question(
                self, "Sil",
                "Bu tekrarlayan görevin hangi instance'larını silmek istiyorsunuz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            # Basit: Yes = tüm seriyi sil, No = sadece bu instance
            if reply == QMessageBox.StandardButton.Yes:
                task_service.delete_task(task_id, delete_recurrence=True)
            elif reply == QMessageBox.StandardButton.No:
                task_service.delete_task(task_id, delete_recurrence=False)
        else:
            reply = QMessageBox.question(
                self, "Sil", f'"{task.title}" silinsin mi?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                task_service.delete_task(task_id)

        self.refresh()

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        """Kapatmak yerine system tray'e gizle."""
        event.ignore()
        self.hide()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
