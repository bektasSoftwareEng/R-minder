"""
Masaüstü widget penceresi.

Progman/WorkerW gömme ile masaüstünde ikonların arkasında görünür.
Sürükle-bırak ile taşınabilir, köşelerden yeniden boyutlandırılabilir.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QSizeGrip, QApplication,
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QCursor

from app.services import task_service
from app.core import repository
from app.ui.widget.tab_view import WidgetTabView
from app.ui.widget.embedder import DesktopEmbedder
from app.utils.config import get_widget_geometry, save_widget_geometry

# Boyutlandırma kenar toleransı (piksel)
_RESIZE_MARGIN = 8


class DesktopWidget(QWidget):
    open_main_window_requested = pyqtSignal()
    add_task_requested         = pyqtSignal()

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("R-minder Widget")

        x, y, w, h = get_widget_geometry()
        self.setGeometry(x, y, w, h)
        self.setMinimumSize(240, 300)

        self._drag_pos: QPoint | None = None
        self._resize_edge: str | None = None

        self._build_ui()
        self._setup_refresh_timer()

        # Masaüstüne göm
        self._embedder = DesktopEmbedder(self, self)
        # Pencere handle'ı hazır olmadan embed çağrılmamalı;
        # ilk show() sonrası embed yapıyoruz.

    # ------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        # İlk gösterimde göm
        QTimer.singleShot(100, self._embed)

    def _embed(self):
        success = self._embedder.embed()
        if success:
            self._embedder.start_watchdog()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Ana kart (arka plan rengi ve border)
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 46, 220);
                border-radius: 10px;
                border: 1px solid #45475A;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # --- Başlık çubuğu (drag alanı) ---
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: rgba(24, 24, 37, 200);
                border-radius: 10px;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
                border-bottom: 1px solid #313244;
            }
        """)
        header.setFixedHeight(38)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 8, 0)

        lbl = QLabel("R-minder")
        lbl.setStyleSheet("color: #89B4FA; font-weight: 700; font-size: 13px; border: none; background: transparent;")
        h_layout.addWidget(lbl)
        h_layout.addStretch()

        btn_add = QPushButton("+")
        btn_add.setObjectName("btn_icon")
        btn_add.setFixedSize(26, 26)
        btn_add.setToolTip("Yeni Görev")
        btn_add.setStyleSheet("font-size: 18px; font-weight: 300; background: transparent; border: none; color: #89B4FA;")
        btn_add.clicked.connect(self.add_task_requested)
        h_layout.addWidget(btn_add)

        btn_open = QPushButton("⊞")
        btn_open.setObjectName("btn_icon")
        btn_open.setFixedSize(26, 26)
        btn_open.setToolTip("Ana pencereyi aç")
        btn_open.setStyleSheet("font-size: 14px; background: transparent; border: none; color: #BAC2DE;")
        btn_open.clicked.connect(self.open_main_window_requested)
        h_layout.addWidget(btn_open)

        card_layout.addWidget(header)

        # --- Sekmeler ---
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab {
                background: transparent;
                color: #6C7086;
                padding: 5px 12px;
                font-size: 11px;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected { color: #89B4FA; border-bottom: 2px solid #89B4FA; }
            QTabBar::tab:hover:!selected { color: #BAC2DE; }
        """)

        self.tab_today    = WidgetTabView()
        self.tab_tomorrow = WidgetTabView()
        self.tab_week     = WidgetTabView()

        self.tabs.addTab(self.tab_today,    "Bugün")
        self.tabs.addTab(self.tab_tomorrow, "Yarın")
        self.tabs.addTab(self.tab_week,     "Bu Hafta")

        for tab in (self.tab_today, self.tab_tomorrow, self.tab_week):
            tab.complete_requested.connect(self._on_complete)
            tab.delete_requested.connect(self._on_delete)

        card_layout.addWidget(self.tabs)

        # Sağ alt köşe boyutlandırma tutamacı
        grip_row = QHBoxLayout()
        grip_row.addStretch()
        grip = QSizeGrip(self)
        grip.setStyleSheet("background: transparent;")
        grip_row.addWidget(grip)
        grip_row.setContentsMargins(0, 0, 2, 2)
        card_layout.addLayout(grip_row)

        root.addWidget(card)

    # ------------------------------------------------------------------
    def _setup_refresh_timer(self):
        self._timer = QTimer(self)
        self._timer.setInterval(60_000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

    def refresh(self):
        self.tab_today.load_tasks(task_service.get_tasks_for_today())
        self.tab_tomorrow.load_tasks(task_service.get_tasks_for_tomorrow())
        self.tab_week.load_tasks(task_service.get_tasks_for_this_week())

        today_count = len(task_service.get_tasks_for_today())
        label = f"Bugün ({today_count})" if today_count else "Bugün"
        self.tabs.setTabText(0, label)

    # ------------------------------------------------------------------
    def _on_complete(self, task_id: int):
        task_service.complete_task(task_id)
        self.refresh()

    def _on_delete(self, task_id: int):
        task_service.delete_task(task_id)
        self.refresh()

    # ------------------------------------------------------------------
    # Sürükleme — başlık çubuğuna tıklayınca
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Sadece üst bar bölgesinde sürüklemeye izin ver
            if event.position().y() < 38:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            # Yeni konumu kaydet
            geo = self.geometry()
            save_widget_geometry(geo.x(), geo.y(), geo.width(), geo.height())
            # Embed sonrası konum güncelle
            if self._embedder._parent_hwnd:
                import ctypes
                ctypes.windll.user32.MoveWindow(
                    self._embedder._hwnd,
                    geo.x(), geo.y(), geo.width(), geo.height(), True
                )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        geo = self.geometry()
        save_widget_geometry(geo.x(), geo.y(), geo.width(), geo.height())

    def closeEvent(self, event):
        """Widget kapatılmasın — sadece gizlensin."""
        event.ignore()
        self.hide()
