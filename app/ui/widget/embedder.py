"""
Windows Progman/WorkerW masaüstü gömme mekanizması.

Pencereyi duvar kağıdının önünde, masaüstü ikonlarının arkasında
sabitler. Explorer yeniden başlarsa watchdog otomatik olarak yeniden gömer.

Windows 10: Progman → 0x052C → WorkerW oluşturulur, widget WorkerW'ye gömülür.
Windows 11: SHELLDLL_DefView Progman'da kalır; widget doğrudan Progman'a
            gömülür ve SetWindowPos ile SHELLDLL_DefView'in arkasına alınır.
"""
import ctypes
import ctypes.wintypes as wintypes
import logging
from PyQt6.QtCore import QTimer, QObject

logger = logging.getLogger(__name__)

_user32 = ctypes.windll.user32
_WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# SetWindowPos flags
_SWP_NOMOVE     = 0x0002
_SWP_NOSIZE     = 0x0001
_SWP_NOACTIVATE = 0x0010


def _find_desktop_layer() -> tuple[int, bool]:
    """
    Widget'ın gömüleceği parent HWND'yi ve Windows 11 modunu döner.

    Returns:
        (parent_hwnd, is_win11_mode)
        - parent_hwnd: SetParent hedefi; 0 ise gömme başarısız.
        - is_win11_mode: True ise Progman'a gömüldü,
          SetWindowPos ile SHELLDLL_DefView'in arkasına alınmalı.
    """
    progman = _user32.FindWindowW("Progman", None)
    if not progman:
        logger.warning("Progman penceresi bulunamadı.")
        return 0, False

    # WorkerW katmanı oluşturması için tetikle
    _user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0, 1000, None)

    # --- Windows 10 klasik yol: WorkerW içinde SHELLDLL_DefView ---
    workerw_result = ctypes.c_size_t(0)

    def _enum(hwnd, _lparam):
        shell_view = _user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        if shell_view:
            workerw = _user32.FindWindowExW(0, hwnd, "WorkerW", None)
            if workerw:
                workerw_result.value = workerw
        return True

    _cb = _WNDENUMPROC(_enum)
    _user32.EnumWindows(_cb, 0)

    if workerw_result.value:
        logger.debug("WorkerW bulundu (Windows 10 modu): %d", workerw_result.value)
        return workerw_result.value, False

    # --- Windows 11 fallback: SHELLDLL_DefView Progman'ın direkt çocuğu ---
    shell_view = _user32.FindWindowExW(progman, 0, "SHELLDLL_DefView", None)
    if shell_view:
        logger.debug("Windows 11 modu: Progman'a gömülüyor (SHELLDLL_DefView=%d).", shell_view)
        return progman, True

    logger.warning("Ne WorkerW ne de SHELLDLL_DefView bulunamadı.")
    return 0, False


class DesktopEmbedder(QObject):
    """
    Verilen Qt penceresini Windows masaüstüne gömer.

    Kullanım:
        embedder = DesktopEmbedder(widget)
        embedder.embed()
        embedder.start_watchdog()
    """

    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self._widget = widget
        self._hwnd: int = int(widget.winId())
        self._parent_hwnd: int = 0
        self._watchdog = QTimer(self)
        self._watchdog.setInterval(5_000)
        self._watchdog.timeout.connect(self._check)

    # ------------------------------------------------------------------
    def embed(self) -> bool:
        """
        Pencereyi masaüstüne gömer.
        Başarılıysa True, hedef bulunamazsa False döner.
        """
        parent_hwnd, is_win11 = _find_desktop_layer()
        if not parent_hwnd:
            return False

        self._parent_hwnd = parent_hwnd
        _user32.SetParent(self._hwnd, parent_hwnd)

        if is_win11:
            # SHELLDLL_DefView (ikonlar) arkasına al
            shell_view = _user32.FindWindowExW(parent_hwnd, 0, "SHELLDLL_DefView", None)
            if shell_view:
                _user32.SetWindowPos(
                    self._hwnd, shell_view, 0, 0, 0, 0,
                    _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOACTIVATE,
                )

        # Konumu uygula
        from app.utils.config import get_widget_geometry
        x, y, w, h = get_widget_geometry()
        _user32.MoveWindow(self._hwnd, x, y, w, h, True)

        # SetParent sonrası Qt pencereyi gizleyebilir — Win32 ile zorla göster
        _SW_SHOW = 5
        _user32.ShowWindow(self._hwnd, _SW_SHOW)
        _user32.UpdateWindow(self._hwnd)

        logger.info(
            "Widget gömüldü: parent=%d win11=%s konum=(%d,%d,%dx%d)",
            parent_hwnd, is_win11, x, y, w, h,
        )
        return True

    def start_watchdog(self) -> None:
        self._watchdog.start()

    def stop_watchdog(self) -> None:
        self._watchdog.stop()

    # ------------------------------------------------------------------
    def _check(self) -> None:
        """Explorer yeniden başladıysa otomatik yeniden göm."""
        if not self._parent_hwnd:
            return
        current_parent = _user32.GetParent(self._hwnd)
        if current_parent != self._parent_hwnd:
            logger.info("Watchdog: parent değişti, yeniden gömülüyor.")
            self.embed()
