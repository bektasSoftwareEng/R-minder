"""
Masaüstü widget penceresi.

Frameless, şeffaf, daima-altta floating window.
Başlık çubuğundaki ▲/▼ butonu ile daraltılıp genişletilebilir.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QSizeGrip,
)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal

from app.services import task_service
from app.ui.widget.tab_view import WidgetTabView
from app.utils.config import get_widget_geometry, save_widget_geometry
from app.utils import config

_HEADER_H   = 38
_BTN_STYLE  = "font-size: {size}px; font-weight: {w}; background: transparent; border: none; color: {c};"


class DesktopWidget(QWidget):
    open_main_window_requested = pyqtSignal()
    add_task_requested         = pyqtSignal()

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnBottomHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("R-minder Widget")

        x, y, w, h = get_widget_geometry()
        self._expanded_height = max(h, 300)
        self._is_collapsed = config.get("widget_collapsed", "0") == "1"

        self._drag_pos: QPoint | None = None

        self._build_ui()
        self._setup_refresh_timer()

        # Başlangıç durumunu uygula (show() öncesi)
        if self._is_collapsed:
            self._apply_collapsed(animate=False)
        else:
            self.setGeometry(x, y, w, self._expanded_height)
            self.setMinimumSize(240, 300)

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._card = QWidget()
        self._card.setObjectName("widget_card")
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # --- Başlık çubuğu ---
        self._header = QWidget()
        self._header.setFixedHeight(_HEADER_H)
        self._header.setObjectName("widget_header")
        h_layout = QHBoxLayout(self._header)
        h_layout.setContentsMargins(10, 0, 8, 0)
        h_layout.setSpacing(2)

        lbl = QLabel("R-minder")
        lbl.setStyleSheet(
            "color: #89B4FA; font-weight: 700; font-size: 13px;"
            "border: none; background: transparent;"
        )
        h_layout.addWidget(lbl)
        h_layout.addStretch()

        btn_add = QPushButton("+")
        btn_add.setFixedSize(26, 26)
        btn_add.setToolTip("Yeni Görev")
        btn_add.setStyleSheet(_BTN_STYLE.format(size=18, w=300, c="#89B4FA"))
        btn_add.clicked.connect(self.add_task_requested)
        h_layout.addWidget(btn_add)

        btn_open = QPushButton("⊞")
        btn_open.setFixedSize(26, 26)
        btn_open.setToolTip("Ana pencereyi aç")
        btn_open.setStyleSheet(_BTN_STYLE.format(size=14, w=400, c="#BAC2DE"))
        btn_open.clicked.connect(self.open_main_window_requested)
        h_layout.addWidget(btn_open)

        self._btn_collapse = QPushButton("▲")
        self._btn_collapse.setFixedSize(26, 26)
        self._btn_collapse.setToolTip("Daralt / Genişlet")
        self._btn_collapse.setStyleSheet(_BTN_STYLE.format(size=11, w=400, c="#6C7086"))
        self._btn_collapse.clicked.connect(self.toggle_collapse)
        h_layout.addWidget(self._btn_collapse)

        card_layout.addWidget(self._header)

        # --- Gövde (sekmeler + grip) — daraltınca gizlenir ---
        self._body = QWidget()
        self._body.setObjectName("widget_body")
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab {
                background: transparent; color: #6C7086;
                padding: 5px 12px; font-size: 11px;
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

        body_layout.addWidget(self.tabs)

        grip_row = QHBoxLayout()
        grip_row.addStretch()
        grip = QSizeGrip(self)
        grip.setStyleSheet("background: transparent;")
        grip_row.addWidget(grip)
        grip_row.setContentsMargins(0, 0, 2, 2)
        body_layout.addLayout(grip_row)

        card_layout.addWidget(self._body)
        root.addWidget(self._card)

        self._update_card_style()

    # ------------------------------------------------------------------
    def toggle_collapse(self):
        self._is_collapsed = not self._is_collapsed
        config.set("widget_collapsed", "1" if self._is_collapsed else "0")
        self._apply_collapsed(animate=True)

    def _apply_collapsed(self, animate: bool = True):
        if self._is_collapsed:
            # Genişletilmiş yüksekliği sakla
            if not animate:
                pass  # __init__'den zaten self._expanded_height set edildi
            else:
                self._expanded_height = self.height()
                save_widget_geometry(
                    self.x(), self.y(),
                    self.width(), self._expanded_height,
                )

            self._body.hide()
            self._btn_collapse.setText("▼")
            self._btn_collapse.setToolTip("Genişlet")
            self.setMinimumSize(240, _HEADER_H)
            self.setMaximumHeight(_HEADER_H)
            self.resize(self.width(), _HEADER_H)
        else:
            self._body.show()
            self._btn_collapse.setText("▲")
            self._btn_collapse.setToolTip("Daralt")
            self.setMaximumHeight(16777215)   # Qt default max
            self.setMinimumSize(240, 300)
            self.resize(self.width(), self._expanded_height)

        self._update_card_style()

    def _update_card_style(self):
        """Daraltılmış/genişletilmiş duruma göre kart stilini güncelle."""
        if self._is_collapsed:
            # Tüm köşeler yuvarlak (alt köşe düzleşmez)
            self._card.setStyleSheet("""
                QWidget#widget_card {
                    background-color: rgba(30, 30, 46, 220);
                    border-radius: 10px;
                    border: 1px solid #45475A;
                }
            """)
            self._header.setStyleSheet("""
                QWidget#widget_header {
                    background-color: rgba(24, 24, 37, 200);
                    border-radius: 10px;
                    border: none;
                }
            """)
        else:
            self._card.setStyleSheet("""
                QWidget#widget_card {
                    background-color: rgba(30, 30, 46, 220);
                    border-radius: 10px;
                    border: 1px solid #45475A;
                }
            """)
            self._header.setStyleSheet("""
                QWidget#widget_header {
                    background-color: rgba(24, 24, 37, 200);
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    border-bottom-left-radius: 0;
                    border-bottom-right-radius: 0;
                    border-bottom: 1px solid #313244;
                }
            """)

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
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < _HEADER_H:
                self._drag_pos = (
                    event.globalPosition().toPoint()
                    - self.frameGeometry().topLeft()
                )

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            if not self._is_collapsed:
                geo = self.geometry()
                save_widget_geometry(geo.x(), geo.y(), geo.width(), geo.height())
            else:
                # Daraltılmışken sadece konumu kaydet
                save_widget_geometry(
                    self.x(), self.y(),
                    self.width(), self._expanded_height,
                )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._is_collapsed:
            geo = self.geometry()
            save_widget_geometry(geo.x(), geo.y(), geo.width(), geo.height())

    def closeEvent(self, event):
        event.ignore()
        self.hide()
