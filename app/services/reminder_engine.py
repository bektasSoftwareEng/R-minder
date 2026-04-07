"""
Arka plan hatırlatıcı motoru.

Her dakika çalışır, saati yaklaşan veya geçmiş görevler için
Windows Toast bildirimi gönderir. Aynı göreve aynı oturumda
birden fazla bildirim gönderilmez.
"""
import logging
from datetime import datetime, date

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from app.core import repository
from app.services import notification_service
from app.utils.config import get_notification_lead_minutes

logger = logging.getLogger(__name__)

# Bildirim türleri
_KIND_DUE     = "due"       # yaklaşan
_KIND_OVERDUE = "overdue"   # gecikmiş


class ReminderEngine(QObject):
    """
    Arka planda çalışan, görev bildirimlerini yöneten motor.

    Kullanım:
        engine = ReminderEngine(parent=app)
        engine.start()
    """

    # Bildirim gönderildiğinde emit edilir — widget/pencere yenileme için
    task_notified = pyqtSignal(int)   # task_id

    def __init__(self, parent=None):
        super().__init__(parent)

        # (task_id, kind) → bu oturumda bildirim gönderildi mi?
        self._notified: set[tuple[int, str]] = set()

        self._timer = QTimer(self)
        self._timer.setInterval(60_000)      # her 60 saniye
        self._timer.timeout.connect(self._check)

    # ------------------------------------------------------------------
    def start(self) -> None:
        """Motoru başlatır. İlk kontrolü hemen yapar."""
        self._check()
        self._timer.start()
        logger.info("ReminderEngine baslatildi.")

    def stop(self) -> None:
        self._timer.stop()
        logger.info("ReminderEngine durduruldu.")

    def reset_notifications(self) -> None:
        """Bildirim geçmişini sıfırlar (uygulama yeniden başlatma simülasyonu)."""
        self._notified.clear()

    # ------------------------------------------------------------------
    def _check(self) -> None:
        lead_minutes = get_notification_lead_minutes()
        now = datetime.now()
        today = date.today()

        try:
            tasks = repository.get_tasks_by_date_range(today, today)
        except Exception as exc:
            logger.error("Gorev sorgusu basarisiz: %s", exc)
            return

        for task in tasks:
            if task.is_completed or task.due_time is None:
                continue

            due_dt = datetime.combine(task.due_date, task.due_time)
            minutes_left = (due_dt - now).total_seconds() / 60

            self._handle_due_soon(task, minutes_left, lead_minutes)
            self._handle_overdue(task, minutes_left)

    # ------------------------------------------------------------------
    def _handle_due_soon(self, task, minutes_left: float, lead_minutes: int) -> None:
        key = (task.id, _KIND_DUE)
        if key in self._notified:
            return
        # Bildirim penceresi: [0, lead_minutes]
        if 0 <= minutes_left <= lead_minutes:
            notification_service.send_due_soon(task.title, int(minutes_left))
            self._notified.add(key)
            self.task_notified.emit(task.id)
            logger.debug("Due-soon bildirimi: task_id=%d, %.1f dk kaldi", task.id, minutes_left)

    def _handle_overdue(self, task, minutes_left: float) -> None:
        key = (task.id, _KIND_OVERDUE)
        if key in self._notified:
            return
        if minutes_left < 0:
            notification_service.send_overdue(task.title)
            self._notified.add(key)
            self.task_notified.emit(task.id)
            logger.debug("Overdue bildirimi: task_id=%d", task.id)
