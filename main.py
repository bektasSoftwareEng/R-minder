import sys
import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from PyQt6.QtWidgets import QApplication

from app.core.database import initialize


def main():
    initialize()

    app = QApplication(sys.argv)
    app.setApplicationName("R-minder")
    app.setQuitOnLastWindowClosed(False)  # System tray'de çalışmaya devam et

    # TODO Faz 2: Main window ve system tray başlatılacak
    # TODO Faz 3: Desktop widget başlatılacak

    print("R-minder başlatıldı. Veritabanı hazır.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
