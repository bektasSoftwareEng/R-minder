import sys
import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app.core.database import initialize
from app.ui.main_window.main_window import MainWindow
from app.ui.widget.desktop_widget import DesktopWidget
from app.ui.system_tray import SystemTray
from app.services.reminder_engine import ReminderEngine


def _load_stylesheet(app: QApplication) -> None:
    qss_path = os.path.join(os.path.dirname(__file__), "app", "ui", "styles", "dark_theme.qss")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass


def main():
    initialize()

    app = QApplication(sys.argv)
    app.setApplicationName("R-minder")
    app.setQuitOnLastWindowClosed(False)

    _load_stylesheet(app)

    # Ana pencere
    window = MainWindow()

    # Masaüstü widget
    widget = DesktopWidget()
    widget.show()
    widget.refresh()

    # Widget → ana pencere bağlantısı
    def open_main_and_add():
        window.show()
        window.raise_()
        window.activateWindow()
        window.open_add_form()

    widget.open_main_window_requested.connect(window.toggle_visibility)
    widget.add_task_requested.connect(open_main_and_add)

    def toggle_widget():
        if widget.isVisible():
            widget.hide()
        else:
            widget.show()
            widget.refresh()

    window.toggle_widget_requested.connect(toggle_widget)

    def reset_widget():
        from app.utils.config import get_widget_geometry
        x, y, w, h = get_widget_geometry()
        widget.setGeometry(x, y, w, h)
        if not widget.isVisible():
            widget.show()
        widget.refresh()

    window.widget_reset_requested.connect(reset_widget)

    # Merkezi yenileme — her veri değişiminde hem pencere hem widget güncellenir
    def refresh_all():
        window.refresh()
        widget.refresh()

    window.data_changed.connect(refresh_all)
    widget.data_changed.connect(refresh_all)

    # System tray
    tray = SystemTray()
    tray.show_main_window_requested.connect(window.toggle_visibility)
    tray.add_task_requested.connect(open_main_and_add)
    tray.quit_requested.connect(app.quit)

    # Bildirim motoru
    engine = ReminderEngine(parent=app)
    engine.task_notified.connect(lambda _: refresh_all())
    engine.start()

    # Ana pencereyi başlangıçta göster (kullanıcı varlığından haberdar olsun)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
