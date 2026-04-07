"""
Windows Progman/WorkerW masaüstü gömme mekanizması.

Pencereyi duvar kağıdının önünde, masaüstü ikonlarının arkasında
sabitler. Explorer yeniden başlarsa watchdog otomatik olarak yeniden gömer.
"""
import ctypes
import ctypes.wintypes as wintypes
from PyQt6.QtCore import QTimer, QObject


_user32 = ctypes.windll.user32
_WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def _find_workerw() -> int | None:
    """WorkerW penceresini bulur; yoksa Progman'a oluşturtur."""
    progman = _user32.FindWindowW("Progman", None)
    if not progman:
        return None

    # Progman'ı WorkerW katmanı oluşturması için tetikle
    _user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0, 1000, None)

    result = ctypes.c_size_t(0)

    def _enum(hwnd, _lparam):
        shell_view = _user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        if shell_view:
            workerw = _user32.FindWindowExW(0, hwnd, "WorkerW", None)
            if workerw:
                result.value = workerw
        return True

    # Callback referansını yerel değişkende sakla — GC'den koru
    _cb = _WNDENUMPROC(_enum)
    _user32.EnumWindows(_cb, 0)
    return result.value or None


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
        self._workerw: int | None = None
        self._watchdog = QTimer(self)
        self._watchdog.setInterval(5_000)   # 5 saniyede bir kontrol
        self._watchdog.timeout.connect(self._check)

    # ------------------------------------------------------------------
    def embed(self) -> bool:
        """
        Pencereyi masaüstüne gömer.
        Başarılıysa True, WorkerW bulunamazsa False döner.
        """
        workerw = _find_workerw()
        if not workerw:
            return False

        self._workerw = workerw
        _user32.SetParent(self._hwnd, workerw)

        # Pencereyi config'den gelen konuma taşı
        from app.utils.config import get_widget_geometry
        x, y, w, h = get_widget_geometry()
        _user32.MoveWindow(self._hwnd, x, y, w, h, True)
        return True

    def start_watchdog(self) -> None:
        self._watchdog.start()

    def stop_watchdog(self) -> None:
        self._watchdog.stop()

    # ------------------------------------------------------------------
    def _check(self) -> None:
        """Explorer yeniden başladıysa otomatik yeniden göm."""
        if self._workerw is None:
            return
        current_parent = _user32.GetParent(self._hwnd)
        if current_parent != self._workerw:
            self.embed()
