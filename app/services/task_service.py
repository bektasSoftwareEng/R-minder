from datetime import date
from typing import Optional

from app.core import repository
from app.core.models import Task, RecurrenceRule
from app.utils.priority import calculate_priority
from app.utils.date_utils import today, tomorrow, week_end


def _enrich(task: Task) -> Task:
    """Göreve öncelik puanı ve tekrarlama kuralı ekler."""
    task.priority = calculate_priority(task)
    if task.recurrence_id:
        task.recurrence_rule = repository.get_recurrence_rule(task.recurrence_id)
    return task


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


def get_tasks_for_today() -> list[Task]:
    tasks = repository.get_tasks_by_date_range(today(), today())
    tasks = [_enrich(t) for t in tasks]
    return sorted(tasks, key=lambda t: -t.priority)


def get_tasks_for_tomorrow() -> list[Task]:
    tasks = repository.get_tasks_by_date_range(tomorrow(), tomorrow())
    tasks = [_enrich(t) for t in tasks]
    return sorted(tasks, key=lambda t: -t.priority)


def get_tasks_for_this_week() -> list[Task]:
    tasks = repository.get_tasks_by_date_range(today(), week_end())
    tasks = [_enrich(t) for t in tasks]
    return sorted(tasks, key=lambda t: (-t.priority, t.due_date))


def get_all_tasks(include_completed: bool = False) -> list[Task]:
    tasks = repository.get_all_tasks(include_completed)
    tasks = [_enrich(t) for t in tasks]
    return sorted(tasks, key=lambda t: (-t.priority, t.due_date))
