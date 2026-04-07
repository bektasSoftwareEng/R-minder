from datetime import date, timedelta
from typing import Iterator

from app.core.models import RecurrenceRule, Task, TaskException
from app.core import repository


def generate_occurrences(rule: RecurrenceRule, from_date: date, to_date: date) -> Iterator[date]:
    """
    Tekrarlama kuralına göre from_date ile to_date arasındaki tüm tarihleri üretir.
    İstisnaları (silinmiş/override edilmiş) hariç tutar.
    """
    exceptions = {
        exc.original_date: exc
        for exc in repository.get_exceptions_for_recurrence(rule.id)
    }

    current = _first_occurrence(rule, from_date)

    while current <= to_date:
        if rule.end_date and current > rule.end_date:
            break

        exc = exceptions.get(current)
        if exc is None:
            yield current
        elif not exc.is_deleted and exc.modified_task_id:
            # Override: değiştirilmiş task ayrıca veritabanında var, burada üretme
            pass

        current = _next_occurrence(rule, current)


def _first_occurrence(rule: RecurrenceRule, from_date: date) -> date:
    """from_date'e eşit veya sonraki ilk tekrarlama tarihini döner."""
    # Basit yaklaşım: from_date'den başla, geçerli bir tarih bulana kadar ilerle
    candidate = from_date
    limit = from_date + timedelta(days=400)
    while candidate <= limit:
        if _matches_rule(rule, candidate):
            return candidate
        candidate += timedelta(days=1)
    return candidate


def _next_occurrence(rule: RecurrenceRule, current: date) -> date:
    """Mevcut tarihten sonraki bir sonraki tekrarlama tarihini döner."""
    if rule.rule_type == "daily":
        return current + timedelta(days=rule.interval)

    if rule.rule_type == "weekly":
        candidate = current + timedelta(days=1)
        limit = current + timedelta(days=7 * rule.interval + 7)
        while candidate <= limit:
            if _matches_rule(rule, candidate):
                return candidate
            candidate += timedelta(days=1)

    if rule.rule_type == "monthly":
        # Aynı gün, N ay sonra
        month = current.month + rule.interval
        year = current.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = rule.day_of_month or current.day
        try:
            return date(year, month, day)
        except ValueError:
            # Ayın son gününe sabitle (örn. 31 Şubat → 28/29 Şubat)
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            return date(year, month, last_day)

    if rule.rule_type == "yearly":
        return date(current.year + rule.interval, current.month, current.day)

    if rule.rule_type == "custom":
        return current + timedelta(days=rule.interval)

    return current + timedelta(days=1)


def _matches_rule(rule: RecurrenceRule, d: date) -> bool:
    """Verilen tarihin tekrarlama kuralıyla eşleşip eşleşmediğini kontrol eder."""
    if rule.rule_type == "daily":
        return True  # Her gün — başlangıç tarihinden itibaren interval ile ilerle

    if rule.rule_type == "weekly":
        if rule.day_of_week:
            day_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            return day_names[d.weekday()] in rule.day_of_week.split(",")
        return True

    if rule.rule_type == "monthly":
        target_day = rule.day_of_month or d.day
        return d.day == target_day

    if rule.rule_type == "yearly":
        return d.month == (rule.month_of_year or d.month) and d.day == d.day

    return True


def create_exception_delete(recurrence_id: int, occurrence_date: date) -> None:
    """Belirli bir instance'ı siler (diğerleri devam eder)."""
    exc = TaskException(
        id=None,
        recurrence_id=recurrence_id,
        original_date=occurrence_date,
        is_deleted=True,
    )
    repository.create_task_exception(exc)


def create_exception_modify(recurrence_id: int, occurrence_date: date, modified_task_id: int) -> None:
    """Belirli bir instance'ı override eder."""
    exc = TaskException(
        id=None,
        recurrence_id=recurrence_id,
        original_date=occurrence_date,
        modified_task_id=modified_task_id,
        is_deleted=False,
    )
    repository.create_task_exception(exc)
