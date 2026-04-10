"""
Windows Toast bildirim servisi.

winotify kütüphanesi üzerinden çalışır.
Winotify mevcut değilse veya hata olursa sessizce geçer.
"""
import logging

logger = logging.getLogger(__name__)

_APP_ID = "R-minder"


def send_toast(title: str, message: str, duration: str = "short") -> None:
    """
    Windows Toast bildirimi gönderir.

    Args:
        title:    Bildirim başlığı
        message:  Bildirim içeriği
        duration: "short" (7sn) veya "long" (25sn)
    """
    try:
        from winotify import Notification, audio

        toast = Notification(
            app_id=_APP_ID,
            title=title,
            msg=message,
            duration=duration,
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except ImportError:
        logger.warning("winotify kurulu degil, bildirim atlanamadi.")
    except Exception as exc:
        logger.error("Toast bildirimi gonderilemedi: %s", exc)


def send_due_soon(task_title: str, minutes_left: int) -> None:
    """Görev zamanı yaklaşıyor bildirimi."""
    if minutes_left <= 1:
        msg = "Görev zamanı geldi!"
    else:
        msg = f"{minutes_left} dakika kaldı."
    send_toast(title=f"⏰ {task_title}", message=msg)


def send_overdue(task_title: str) -> None:
    """Görev gecikmiş bildirimi."""
    send_toast(
        title=f"⚠️ Gecikmiş: {task_title}",
        message="Bu görevin zamanı geçti.",
        duration="long",
    )
