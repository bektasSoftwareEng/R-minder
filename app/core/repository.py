import sqlite3
from datetime import date, time, datetime
from typing import Optional

from app.core.database import get_connection
from app.core.models import Task, RecurrenceRule, TaskException


# ---------------------------------------------------------------------------
# Yardımcı dönüşüm fonksiyonları
# ---------------------------------------------------------------------------

def _row_to_recurrence(row: sqlite3.Row) -> RecurrenceRule:
    return RecurrenceRule(
        id=row["id"],
        rule_type=row["rule_type"],
        interval=row["interval"],
        day_of_week=row["day_of_week"],
        day_of_month=row["day_of_month"],
        month_of_year=row["month_of_year"],
        end_date=date.fromisoformat(row["end_date"]) if row["end_date"] else None,
        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
    )


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        due_date=date.fromisoformat(row["due_date"]),
        due_time=time.fromisoformat(row["due_time"]) if row["due_time"] else None,
        is_completed=bool(row["is_completed"]),
        completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
        recurrence_id=row["recurrence_id"],
        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
    )


# ---------------------------------------------------------------------------
# Görev (Task) CRUD
# ---------------------------------------------------------------------------

def create_task(task: Task) -> Task:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks (title, description, due_date, due_time, recurrence_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task.title,
                task.description,
                task.due_date.isoformat(),
                task.due_time.isoformat() if task.due_time else None,
                task.recurrence_id,
            ),
        )
        task.id = cursor.lastrowid
    return task


def get_task(task_id: int) -> Optional[Task]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_task(row) if row else None


def get_tasks_by_date_range(start: date, end: date) -> list[Task]:
    """Belirtilen tarih aralığındaki tamamlanmamış görevleri döner."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE due_date BETWEEN ? AND ?
              AND is_completed = 0
            ORDER BY due_date, due_time NULLS LAST
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    return [_row_to_task(r) for r in rows]


def get_all_tasks(include_completed: bool = False) -> list[Task]:
    with get_connection() as conn:
        query = "SELECT * FROM tasks"
        if not include_completed:
            query += " WHERE is_completed = 0"
        query += " ORDER BY due_date, due_time NULLS LAST"
        rows = conn.execute(query).fetchall()
    return [_row_to_task(r) for r in rows]


def update_task(task: Task) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?, due_time = ?,
                recurrence_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                task.title,
                task.description,
                task.due_date.isoformat(),
                task.due_time.isoformat() if task.due_time else None,
                task.recurrence_id,
                task.id,
            ),
        )


def complete_task(task_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET is_completed = 1, completed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (task_id,),
        )


def delete_task(task_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


# ---------------------------------------------------------------------------
# Tekrarlama Kuralı (RecurrenceRule) CRUD
# ---------------------------------------------------------------------------

def create_recurrence_rule(rule: RecurrenceRule) -> RecurrenceRule:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO recurrence_rules
                (rule_type, interval, day_of_week, day_of_month, month_of_year, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                rule.rule_type,
                rule.interval,
                rule.day_of_week,
                rule.day_of_month,
                rule.month_of_year,
                rule.end_date.isoformat() if rule.end_date else None,
            ),
        )
        rule.id = cursor.lastrowid
    return rule


def get_recurrence_rule(rule_id: int) -> Optional[RecurrenceRule]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM recurrence_rules WHERE id = ?", (rule_id,)
        ).fetchone()
    return _row_to_recurrence(row) if row else None


def update_recurrence_rule(rule: RecurrenceRule) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE recurrence_rules
            SET rule_type = ?, interval = ?, day_of_week = ?,
                day_of_month = ?, month_of_year = ?, end_date = ?
            WHERE id = ?
            """,
            (
                rule.rule_type,
                rule.interval,
                rule.day_of_week,
                rule.day_of_month,
                rule.month_of_year,
                rule.end_date.isoformat() if rule.end_date else None,
                rule.id,
            ),
        )


def delete_recurrence_rule(rule_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM recurrence_rules WHERE id = ?", (rule_id,))


# ---------------------------------------------------------------------------
# İstisna (TaskException) CRUD
# ---------------------------------------------------------------------------

def create_task_exception(exc: TaskException) -> TaskException:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_exceptions (recurrence_id, original_date, modified_task_id, is_deleted)
            VALUES (?, ?, ?, ?)
            """,
            (exc.recurrence_id, exc.original_date.isoformat(), exc.modified_task_id, exc.is_deleted),
        )
        exc.id = cursor.lastrowid
    return exc


def get_exceptions_for_recurrence(recurrence_id: int) -> list[TaskException]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM task_exceptions WHERE recurrence_id = ?", (recurrence_id,)
        ).fetchall()
    return [
        TaskException(
            id=r["id"],
            recurrence_id=r["recurrence_id"],
            original_date=date.fromisoformat(r["original_date"]),
            modified_task_id=r["modified_task_id"],
            is_deleted=bool(r["is_deleted"]),
            created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else None,
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Ayarlar (Settings)
# ---------------------------------------------------------------------------

def get_setting(key: str) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
