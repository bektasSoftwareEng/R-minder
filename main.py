import sys
import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app.core.database import initialize
from app.ui.main_window.main_window import MainWindow
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

    window = MainWindow()
    window.show()

    tray = SystemTray()
    tray.show_main_window_requested.connect(window.toggle_visibility)
    tray.add_task_requested.connect(window.open_add_form)
    tray.quit_requested.connect(app.quit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
