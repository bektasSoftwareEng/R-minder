from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional


@dataclass
class RecurrenceRule:
    id: Optional[int]
    rule_type: str          # 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom'
    interval: int = 1       # her N günde/haftada/ayda bir
    day_of_week: Optional[str] = None   # 'MON,WED,FRI' — haftalık için
    day_of_month: Optional[int] = None  # 1-31 — aylık için
    month_of_year: Optional[int] = None # 1-12 — yıllık için
    end_date: Optional[date] = None
    created_at: Optional[datetime] = None


@dataclass
class Task:
    id: Optional[int]
    title: str
    due_date: date
    description: Optional[str] = None
    due_time: Optional[time] = None     # None ise sadece tarih bazlı
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    recurrence_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Veritabanında saklanmaz, çalışma zamanında hesaplanır
    priority: int = 0
    recurrence_rule: Optional[RecurrenceRule] = field(default=None, repr=False)


@dataclass
class TaskException:
    """Tekrarlayan görevin belirli bir instance'ının override veya silinmesi."""
    id: Optional[int]
    recurrence_id: int
    original_date: date
    modified_task_id: Optional[int] = None  # None ise sadece silindi
    is_deleted: bool = False
    created_at: Optional[datetime] = None
