"""
Ayarlar diyalogu.

- Bildirim öncesi süre
- Widget konumunu sıfırla
- Windows'ta otomatik başlat
"""
import sys
import os
import winreg
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QCheckBox, QGroupBox, QMessageBox,
)
from PyQt6.QtCore import Qt

from app.utils import config

logger = logging.getLogger(__name__)

_REG_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Run"
_REG_NAME = "R-minder"


def _exe_path() -> str:
    """Çalıştırılabilir dosyanın tam yolunu döner."""
    if getattr(sys, "frozen", False):          # PyInstaller .exe
        return sys.executable
    return f'"{sys.executable}" "{os.path.abspath("main.py")}"'


def _is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, _REG_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def _set_autostart(enable: bool) -> None:
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _REG_KEY, 0, winreg.KEY_SET_VALUE
    )
    if enable:
        winreg.SetValueEx(key, _REG_NAME, 0, winreg.REG_SZ, _exe_path())
    else:
        try:
            winreg.DeleteValue(key, _REG_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)


class SettingsDialog(QDialog):
    def __init__(self, on_widget_reset=None, parent=None):
        super().__init__(parent)
        self._on_widget_reset = on_widget_reset
        self.setWindowTitle("Ayarlar")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # --- Bildirimler ---
        grp_notif = QGroupBox("Bildirimler")
        notif_layout = QVBoxLayout(grp_notif)
        notif_layout.setSpacing(10)

        row = QHBoxLayout()
        row.addWidget(QLabel("Görev zamanından kaç dakika önce bildir:"))
        self.spin_lead = QSpinBox()
        self.spin_lead.setRange(1, 120)
        self.spin_lead.setSuffix(" dk")
        self.spin_lead.setValue(config.get_notification_lead_minutes())
        row.addWidget(self.spin_lead)
        notif_layout.addLayout(row)
        root.addWidget(grp_notif)

        # --- Widget ---
        grp_widget = QGroupBox("Masaüstü Widget")
        widget_layout = QVBoxLayout(grp_widget)
        widget_layout.setSpacing(10)

        btn_reset = QPushButton("Konumu Sıfırla")
        btn_reset.setObjectName("btn_secondary")
        btn_reset.clicked.connect(self._reset_widget_pos)
        widget_layout.addWidget(btn_reset)
        root.addWidget(grp_widget)

        # --- Başlangıç ---
        grp_startup = QGroupBox("Sistem")
        startup_layout = QVBoxLayout(grp_startup)

        self.chk_autostart = QCheckBox("Windows başlangıcında otomatik çalıştır")
        self.chk_autostart.setChecked(_is_autostart_enabled())
        startup_layout.addWidget(self.chk_autostart)
        root.addWidget(grp_startup)

        # --- Butonlar ---
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("İptal")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    def _reset_widget_pos(self):
        config.save_widget_geometry(40, 40, 320, 520)
        if self._on_widget_reset:
            self._on_widget_reset()
        QMessageBox.information(self, "Widget", "Widget konumu sıfırlandı.")

    def _save(self):
        config.set("notification_lead_minutes", str(self.spin_lead.value()))
        try:
            _set_autostart(self.chk_autostart.isChecked())
        except Exception as exc:
            logger.warning("Autostart ayarlanamadı: %s", exc)
            QMessageBox.warning(self, "Uyarı", f"Başlangıç ayarı değiştirilemedi:\n{exc}")
        self.accept()
