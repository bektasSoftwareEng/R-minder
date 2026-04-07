from app.utils.date_utils import minutes_until
from app.core.models import Task


# Öncelik seviyeleri (yüksek = daha acil)
PRIORITY_OVERDUE = 5
PRIORITY_CRITICAL = 4   # < 2 saat
PRIORITY_HIGH = 3        # 2–24 saat
PRIORITY_TODAY = 2       # bugün, saatsiz
PRIORITY_NORMAL = 1
PRIORITY_COMPLETED = 0


def calculate_priority(task: Task) -> int:
    if task.is_completed:
        return PRIORITY_COMPLETED

    minutes = minutes_until(task.due_date, task.due_time)

    if minutes < 0:
        return PRIORITY_OVERDUE

    if task.due_time is not None:
        if minutes < 120:
            return PRIORITY_CRITICAL
        if minutes < 1440:
            return PRIORITY_HIGH

    from app.utils.date_utils import is_today
    if is_today(task.due_date):
        return PRIORITY_TODAY

    return PRIORITY_NORMAL


# Renk sabitleri (öncelik seviyesi → HEX renk kodu)
PRIORITY_COLORS = {
    PRIORITY_OVERDUE:   "#FF4444",  # Kırmızı
    PRIORITY_CRITICAL:  "#FF8C00",  # Turuncu
    PRIORITY_HIGH:      "#FFD700",  # Sarı
    PRIORITY_TODAY:     "#4FC3F7",  # Açık mavi
    PRIORITY_NORMAL:    "#E0E0E0",  # Gri-beyaz
    PRIORITY_COMPLETED: "#757575",  # Soluk gri
}


def get_color(priority: int) -> str:
    return PRIORITY_COLORS.get(priority, PRIORITY_COLORS[PRIORITY_NORMAL])
