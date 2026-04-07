from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QObject


def _make_tray_icon() -> QIcon:
    """Assets yokken programatik olarak basit bir ikon üretir."""
    px = QPixmap(32, 32)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#89B4FA"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    painter.setBrush(QColor("#1E1E2E"))
    # İçi: basit saat/takvim simgesi gibi beyaz dikdörtgen
    painter.drawRect(10, 9, 12, 14)
    painter.setBrush(QColor("#89B4FA"))
    painter.drawRect(12, 13, 8, 2)
    painter.drawRect(12, 17, 6, 2)
    painter.end()
    return QIcon(px)


class SystemTray(QObject):
    show_main_window_requested = pyqtSignal()
    add_task_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._tray = QSystemTrayIcon(parent)
        self._tray.setIcon(_make_tray_icon())
        self._tray.setToolTip("R-minder")

        menu = QMenu()
        action_show = menu.addAction("Göster / Gizle")
        action_add  = menu.addAction("Yeni Görev Ekle")
        menu.addSeparator()
        action_quit = menu.addAction("Çıkış")

        action_show.triggered.connect(self.show_main_window_requested)
        action_add.triggered.connect(self.add_task_requested)
        action_quit.triggered.connect(self.quit_requested)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_activated)
        self._tray.show()

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window_requested.emit()

    def show_message(self, title: str, message: str) -> None:
        self._tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 4000)
