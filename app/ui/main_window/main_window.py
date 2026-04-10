from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from app.services import task_service
from app.core import repository
from app.ui.main_window.task_list import TaskListWidget
from app.ui.main_window.task_form import TaskForm
from app.ui.main_window.recurrence_action_dialog import RecurrenceActionDialog
from app.services import recurrence_service


class MainWindow(QMainWindow):
    toggle_widget_requested = pyqtSignal()

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

        btn_widget = QPushButton("⊞ Widget")
        btn_widget.setObjectName("btn_secondary")
        btn_widget.setToolTip("Masaüstü widget'ı göster/gizle")
        btn_widget.clicked.connect(self.toggle_widget_requested)
        h_layout.addWidget(btn_widget)

        btn_settings = QPushButton("⚙")
        btn_settings.setObjectName("btn_icon")
        btn_settings.setToolTip("Ayarlar")
        btn_settings.setFixedSize(36, 36)
        btn_settings.clicked.connect(self._open_settings)
        h_layout.addWidget(btn_settings)

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
        if task is None:
            return

        if task.recurrence_id:
            task.recurrence_rule = repository.get_recurrence_rule(task.recurrence_id)
            dlg = RecurrenceActionDialog("edit", task.title, parent=self)
            choice = dlg.exec()
            if choice == RecurrenceActionDialog.ONLY_THIS:
                self._edit_single_instance(task)
            elif choice == RecurrenceActionDialog.ALL_SERIES:
                self._edit_full_series(task)
        else:
            self.open_add_form(task)

    def _edit_single_instance(self, task):
        """Bu instance'ı seridenden kopararak bağımsız olarak düzenle."""
        form = TaskForm(self, task, show_recurrence=False)
        if form.exec():
            data = form.get_data()
            task.title       = data["title"]
            task.description = data["description"]
            task.due_date    = data["due_date"]
            task.due_time    = data["due_time"]
            task.recurrence_id = None          # seriden kopar
            task_service.update_task(task)
            self.refresh()

    def _edit_full_series(self, task):
        """Görevin tüm serisini (kural dahil) düzenle."""
        form = TaskForm(self, task, show_recurrence=True)
        if form.exec():
            data = form.get_data()
            task.title       = data["title"]
            task.description = data["description"]
            task.due_date    = data["due_date"]
            task.due_time    = data["due_time"]
            new_rule = data["recurrence_rule"]
            if new_rule and task.recurrence_id:
                new_rule.id = task.recurrence_id
                repository.update_recurrence_rule(new_rule)
            elif new_rule:
                saved = repository.create_recurrence_rule(new_rule)
                task.recurrence_id = saved.id
            else:
                # Tekrarlama kaldırıldı
                if task.recurrence_id:
                    repository.delete_recurrence_rule(task.recurrence_id)
                task.recurrence_id = None
            task_service.update_task(task)
            self.refresh()

    def _on_delete(self, task_id: int):
        task = repository.get_task(task_id)
        if task is None:
            return

        if task.recurrence_id:
            dlg = RecurrenceActionDialog("delete", task.title, parent=self)
            choice = dlg.exec()
            if choice == RecurrenceActionDialog.ONLY_THIS:
                # Sadece bu instance: task_exceptions'a işle, task kaydını sil
                recurrence_service.create_exception_delete(task.recurrence_id, task.due_date)
                task_service.delete_task(task_id, delete_recurrence=False)
            elif choice == RecurrenceActionDialog.ALL_SERIES:
                task_service.delete_task(task_id, delete_recurrence=True)
            else:
                return
        else:
            reply = QMessageBox.question(
                self, "Sil", f'"{task.title}" silinsin mi?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            task_service.delete_task(task_id)

        self.refresh()

    def _open_settings(self):
        from app.ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(
            on_widget_reset=lambda: self.toggle_widget_requested.emit(),
            parent=self,
        )
        dlg.exec()

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
