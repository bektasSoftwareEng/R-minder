import copy
from datetime import date
from typing import Optional

from app.core import repository
from app.core.models import Task, RecurrenceRule
from app.utils.priority import calculate_priority
from app.utils.date_utils import today, tomorrow, week_end
from app.services import recurrence_service


def _enrich(task: Task) -> Task:
    """Göreve öncelik puanı ve tekrarlama kuralı ekler."""
    task.priority = calculate_priority(task)
    if task.recurrence_id and task.recurrence_rule is None:
        task.recurrence_rule = repository.get_recurrence_rule(task.recurrence_id)
    return task


def _occurrences_in_range(start: date, end: date) -> list[Task]:
    """
    Tekrarlayan görevlerin start-end arasına düşen sanal occurrence'larını üretir.

    Tüm recurring görünürlük bu fonksiyon üzerinden geçer; direkt DB sorgusu
    recurring task'ları döndürmez. Bu sayede task_exceptions her tarih için
    (seed'in due_date'i dahil) doğru çalışır.

    - Seri başlangıcı (base.due_date) öncesi occurrence üretilmez.
    - Her occurrence için base task'ın sığ kopyası döner, due_date değiştirilir.
    """
    result: list[Task] = []

    for base in repository.get_recurring_tasks():
        rule = repository.get_recurrence_rule(base.recurrence_id)
        if rule is None:
            continue
        base.recurrence_rule = rule

        # Seri kendi başlangıç tarihinden önce görünmemeli
        effective_start = max(start, base.due_date)
        if effective_start > end:
            continue

        for occ_date in recurrence_service.generate_occurrences(rule, effective_start, end):
            virtual = copy.copy(base)
            virtual.due_date = occ_date
            result.append(virtual)

    return result


def create_task(
    title: str,
    due_date: date,
    description: str = "",
    due_time=None,
    recurrence_rule: Optional[RecurrenceRule] = None,
) -> Task:
    rule_id = None
    if recurrence_rule is not None:
        rule = repository.create_recurrence_rule(recurrence_rule)
        rule_id = rule.id

    task = Task(
        id=None,
        title=title,
        description=description or None,
        due_date=due_date,
        due_time=due_time,
        recurrence_id=rule_id,
    )
    return _enrich(repository.create_task(task))


def update_task(task: Task) -> None:
    repository.update_task(task)


def complete_task(task_id: int) -> None:
    repository.complete_task(task_id)


def delete_task(task_id: int, delete_recurrence: bool = False) -> None:
    task = repository.get_task(task_id)
    repository.delete_task(task_id)
    if delete_recurrence and task and task.recurrence_id:
        repository.delete_recurrence_rule(task.recurrence_id)


def _non_recurring_in_range(start: date, end: date) -> list[Task]:
    """Sadece tekrarlamayan görevleri döner (recurring'ler _occurrences_in_range'den gelir)."""
    return [t for t in repository.get_tasks_by_date_range(start, end)
            if t.recurrence_id is None]


def get_tasks_for_today() -> list[Task]:
    _today = today()
    tasks = _non_recurring_in_range(_today, _today)
    tasks += _occurrences_in_range(_today, _today)
    return sorted([_enrich(t) for t in tasks], key=lambda t: -t.priority)


def get_tasks_for_tomorrow() -> list[Task]:
    _tomorrow = tomorrow()
    tasks = _non_recurring_in_range(_tomorrow, _tomorrow)
    tasks += _occurrences_in_range(_tomorrow, _tomorrow)
    return sorted([_enrich(t) for t in tasks], key=lambda t: -t.priority)


def get_tasks_for_this_week() -> list[Task]:
    _today = today()
    _end = week_end()
    tasks = _non_recurring_in_range(_today, _end)
    tasks += _occurrences_in_range(_today, _end)
    return sorted([_enrich(t) for t in tasks], key=lambda t: (-t.priority, t.due_date))


def get_all_tasks(include_completed: bool = False) -> list[Task]:
    tasks = repository.get_all_tasks(include_completed)
    return sorted([_enrich(t) for t in tasks], key=lambda t: (-t.priority, t.due_date))
