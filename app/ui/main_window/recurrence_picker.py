from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QDateEdit, QCheckBox, QGroupBox,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import date

from app.core.models import RecurrenceRule


RULE_TYPES = ["Tekrar yok", "Günlük", "Haftalık", "Aylık", "Yıllık", "Özel (N günde bir)"]
RULE_KEYS  = [None, "daily", "weekly", "monthly", "yearly", "custom"]

DAY_LABELS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
DAY_KEYS   = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


class RecurrencePicker(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._on_type_changed(0)

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Tekrar tipi
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Tekrar:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(RULE_TYPES)
        self.combo_type.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self.combo_type)
        type_row.addStretch()
        root.addLayout(type_row)

        # Detay grubu
        self.group = QGroupBox("Tekrarlama Ayarları")
        group_layout = QVBoxLayout(self.group)
        group_layout.setSpacing(8)

        # Aralık (her N ...)
        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("Her"))
        self.spin_interval = QSpinBox()
        self.spin_interval.setMinimum(1)
        self.spin_interval.setMaximum(365)
        self.spin_interval.setValue(1)
        interval_row.addWidget(self.spin_interval)
        self.lbl_interval_unit = QLabel("gün(de) bir")
        interval_row.addWidget(self.lbl_interval_unit)
        interval_row.addStretch()
        group_layout.addLayout(interval_row)

        # Haftalık: gün seçimi
        self.week_widget = QWidget()
        week_row = QHBoxLayout(self.week_widget)
        week_row.setContentsMargins(0, 0, 0, 0)
        week_row.setSpacing(4)
        self._day_checks = []
        for label in DAY_LABELS:
            cb = QCheckBox(label)
            self._day_checks.append(cb)
            week_row.addWidget(cb)
        week_row.addStretch()
        group_layout.addWidget(self.week_widget)

        # Aylık: ayın kaçı
        self.month_widget = QWidget()
        month_row = QHBoxLayout(self.month_widget)
        month_row.setContentsMargins(0, 0, 0, 0)
        month_row.addWidget(QLabel("Ayın"))
        self.spin_day_of_month = QSpinBox()
        self.spin_day_of_month.setMinimum(1)
        self.spin_day_of_month.setMaximum(31)
        month_row.addWidget(self.spin_day_of_month)
        month_row.addWidget(QLabel(". günü"))
        month_row.addStretch()
        group_layout.addWidget(self.month_widget)

        # Bitiş tarihi
        end_row = QHBoxLayout()
        self.chk_end_date = QCheckBox("Bitiş tarihi:")
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate().addYears(1))
        self.date_end.setEnabled(False)
        self.chk_end_date.toggled.connect(self.date_end.setEnabled)
        end_row.addWidget(self.chk_end_date)
        end_row.addWidget(self.date_end)
        end_row.addStretch()
        group_layout.addLayout(end_row)

        root.addWidget(self.group)

    # ------------------------------------------------------------------
    def _on_type_changed(self, index: int):
        has_recurrence = index > 0
        self.group.setVisible(has_recurrence)

        is_weekly  = RULE_KEYS[index] == "weekly"
        is_monthly = RULE_KEYS[index] == "monthly"
        is_custom  = RULE_KEYS[index] == "custom"

        self.week_widget.setVisible(is_weekly)
        self.month_widget.setVisible(is_monthly)

        # Aralık spinbox sadece daily/custom/weekly(interval) için göster
        show_interval = RULE_KEYS[index] in ("daily", "weekly", "custom")
        self.spin_interval.setVisible(show_interval)
        self.lbl_interval_unit.setVisible(show_interval)

        units = {"daily": "gün(de) bir", "weekly": "hafta(da) bir", "custom": "gün(de) bir"}
        self.lbl_interval_unit.setText(units.get(RULE_KEYS[index], ""))

        self.changed.emit()

    # ------------------------------------------------------------------
    def get_rule(self) -> RecurrenceRule | None:
        idx = self.combo_type.currentIndex()
        rule_type = RULE_KEYS[idx]
        if rule_type is None:
            return None

        day_of_week = None
        if rule_type == "weekly":
            selected = [DAY_KEYS[i] for i, cb in enumerate(self._day_checks) if cb.isChecked()]
            day_of_week = ",".join(selected) if selected else None

        end_date = None
        if self.chk_end_date.isChecked():
            qd = self.date_end.date()
            end_date = date(qd.year(), qd.month(), qd.day())

        return RecurrenceRule(
            id=None,
            rule_type=rule_type,
            interval=self.spin_interval.value(),
            day_of_week=day_of_week,
            day_of_month=self.spin_day_of_month.value() if rule_type == "monthly" else None,
            end_date=end_date,
        )

    def set_rule(self, rule: RecurrenceRule | None):
        if rule is None:
            self.combo_type.setCurrentIndex(0)
            return
        key = rule.rule_type
        if key in RULE_KEYS:
            self.combo_type.setCurrentIndex(RULE_KEYS.index(key))
        self.spin_interval.setValue(rule.interval)
        if rule.day_of_week:
            days = rule.day_of_week.split(",")
            for i, cb in enumerate(self._day_checks):
                cb.setChecked(DAY_KEYS[i] in days)
        if rule.day_of_month:
            self.spin_day_of_month.setValue(rule.day_of_month)
        if rule.end_date:
            self.chk_end_date.setChecked(True)
            self.date_end.setDate(QDate(rule.end_date.year, rule.end_date.month, rule.end_date.day))
