import sys
import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app.core.database import initialize
from app.ui.main_window.main_window import MainWindow
from app.ui.widget.desktop_widget import DesktopWidget
from app.ui.system_tray import SystemTray


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

    # Widget, ana penceredeki değişikliklerden haberdar olsun
    # (MainWindow refresh sonrası widget da yenilensin)
    original_refresh = window.refresh
    def _refresh_both():
        original_refresh()
        widget.refresh()
    window.refresh = _refresh_both

    # System tray
    tray = SystemTray()
    tray.show_main_window_requested.connect(window.toggle_visibility)
    tray.add_task_requested.connect(open_main_and_add)
    tray.quit_requested.connect(app.quit)

    # Ana pencereyi başlangıçta gizli tut (sadece widget görünsün)
    # İlk açılışta göster ki kullanıcı varlığından haberdar olsun
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
