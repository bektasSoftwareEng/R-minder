from datetime import date, datetime, timedelta


def today() -> date:
    return date.today()


def tomorrow() -> date:
    return date.today() + timedelta(days=1)


def week_end() -> date:
    """Bu haftanın Pazar günü (bugün dahil)."""
    d = date.today()
    return d + timedelta(days=(6 - d.weekday()))


def is_today(d: date) -> bool:
    return d == date.today()


def is_tomorrow(d: date) -> bool:
    return d == tomorrow()


def is_this_week(d: date) -> bool:
    return date.today() <= d <= week_end()


def minutes_until(target_date: date, target_time=None) -> float:
    """Hedefe kaç dakika kaldığını döner. Geçmişse negatif."""
    if target_time is None:
        target_dt = datetime.combine(target_date, datetime.max.time())
    else:
        target_dt = datetime.combine(target_date, target_time)
    delta = target_dt - datetime.now()
    return delta.total_seconds() / 60
