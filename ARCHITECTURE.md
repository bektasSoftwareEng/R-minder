# R-minder — Sistem Mimarisi

## Genel Bakış

R-minder, Windows masaüstünde her zaman görünür bir floating widget ve tam özellikli bir ana pencereden oluşan, modüler yapıda geliştirilmiş bir hatırlatıcı masaüstü uygulamasıdır.

**Teknoloji Yığını:**
- Python 3.11+
- PyQt6 (UI framework)
- SQLite (veri depolama)
- winotify (Windows Toast bildirimleri)

---

## Katman Yapısı

```
┌─────────────────────────────────────────────────────┐
│                    UI LAYER                          │
│  ┌─────────────────┐    ┌──────────────────────┐    │
│  │  Desktop Widget │    │    Main Window        │    │
│  │  (floating,     │    │  (System Tray → App)  │    │
│  │  stays-on-btm)  │    │  Full CRUD + Settings │    │
│  │  Today/Tomorrow │    │                       │    │
│  │  /This Week tabs│    │                       │    │
│  └────────┬────────┘    └──────────┬────────────┘   │
└───────────┼─────────────────────────┼───────────────┘
            │  data_changed (signal)  │
            └──────────┬─────────────┘
                       │ refresh_all() in main.py
┌──────────────────────▼──────────────────────────────┐
│                  SERVICE LAYER                       │
│  TaskService │ NotificationService │ ReminderEngine  │
│  (iş mantığı, öncelik hesaplama, tekrarlama)         │
└───────────────────────────┬─────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────┐
│                  CORE / DATA LAYER                   │
│     Repository (CRUD) │ Models │ Database (SQLite)   │
└─────────────────────────────────────────────────────┘
```

---

## Klasör Yapısı

```
R-minder/
├── main.py                          # Entry point, uygulama bootstrap
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py              # SQLite bağlantı yönetimi, migration
│   │   ├── models.py                # Task, RecurrenceRule, TaskException dataclass'ları
│   │   └── repository.py           # Tüm CRUD operasyonları
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py          # İş mantığı, öncelik hesaplama, occurrence üretimi
│   │   ├── recurrence_service.py    # Tekrarlama genişletme, exception yönetimi
│   │   ├── notification_service.py  # Windows Toast bildirimleri
│   │   └── reminder_engine.py       # Arka plan thread, zamanlayıcı
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── widget/
│   │   │   ├── __init__.py
│   │   │   ├── desktop_widget.py    # Floating widget (WindowStaysOnBottomHint)
│   │   │   ├── embedder.py          # Win32/ctypes Progman kodu (pasif, Windows 11 uyumsuz)
│   │   │   ├── task_card.py         # Tekil görev bileşeni
│   │   │   └── tab_view.py          # Bugün / Yarın / Bu Hafta sekmeleri
│   │   ├── main_window/
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py       # Ana uygulama penceresi
│   │   │   ├── task_form.py         # Ekle / Düzenle formu
│   │   │   ├── task_list.py         # Tam görev listesi görünümü
│   │   │   ├── recurrence_picker.py # Tekrarlama pattern seçici UI
│   │   │   └── recurrence_action_dialog.py  # "Sadece bu / Tüm seri" seçim dialogu
│   │   ├── settings_dialog.py       # Bildirim süresi, widget sıfırlama, autostart
│   │   ├── system_tray.py           # System tray ikonu ve menüsü
│   │   └── styles/
│   │       ├── dark_theme.qss       # Koyu tema stylesheet
│   │       └── colors.py            # Öncelik renk sabitleri
│   └── utils/
│       ├── __init__.py
│       ├── date_utils.py            # Tarih/saat yardımcı fonksiyonlar
│       ├── priority.py              # Aciliyet hesaplama mantığı
│       └── config.py                # Widget konum/boyut, uygulama ayarları
├── data/
│   └── rminder.db                   # SQLite veritabanı
├── assets/
│   └── icons/
├── requirements.txt
├── ARCHITECTURE.md
├── ROADMAP.md
└── TODO.md
```

---

## Veritabanı Şeması

```sql
CREATE TABLE tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    description     TEXT,
    due_date        DATE NOT NULL,
    due_time        TIME,
    is_completed    BOOLEAN DEFAULT 0,
    completed_at    DATETIME,
    recurrence_id   INTEGER REFERENCES recurrence_rules(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recurrence_rules (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type       TEXT NOT NULL,   -- 'daily','weekly','monthly','yearly','custom'
    interval        INTEGER DEFAULT 1,
    day_of_week     TEXT,            -- haftalık: 'MON,WED,FRI'
    day_of_month    INTEGER,         -- aylık: ayın kaçında (1-31)
    month_of_year   INTEGER,         -- yıllık: hangi ay
    end_date        DATE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_exceptions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    recurrence_id    INTEGER NOT NULL REFERENCES recurrence_rules(id),
    original_date    DATE NOT NULL,
    modified_task_id INTEGER REFERENCES tasks(id),  -- override edilmiş yeni task
    is_deleted       BOOLEAN DEFAULT 0,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    key     TEXT PRIMARY KEY,
    value   TEXT
);
```

---

## Öncelik & Renk Sistemi

| Durum | Renk | Widget Davranışı |
|---|---|---|
| Saati yok, bugün değil | Beyaz / gri | Normal sıra |
| Bugün, saati yok | Açık mavi | Üste çık |
| 2–24 saat kaldı | Sarı / turuncu | Daha üste çık |
| < 2 saat kaldı | Turuncu / kırmızı | En üste çık |
| Gecikmiş (overdue) | Kırmızı | Mutlak en üst |
| Tamamlandı | Üstü çizili, soluk | Listenin altı |

Öncelik değeri `task_service.py` içindeki `calculate_priority()` fonksiyonu tarafından anlık hesaplanır, veritabanında saklanmaz.

---

## Widget — Masaüstü Konumlandırma

Windows 11'de `SetParent` ile Progman/WorkerW'ya gömme denenmiş ancak çalışmadığı görülmüştür:
- `SHELLDLL_DefView`, Windows 11'de WorkerW altına taşınmaz — Progman'ın doğrudan child'ı kalır.
- `SetParent` çağrısı sonrası Qt pencereyi gizliyor; `ShowWindow` + `UpdateWindow` çağrıları işe yaramadı.

**Mevcut yaklaşım:** `Qt.WindowType.WindowStaysOnBottomHint` ile frameless, şeffaf arka planlı bir floating window. Her masaüstü penceresinin arkasında kalır, normal pencerelerin önünde görünür. Kod `desktop_widget.py` içindedir; `embedder.py` pasif bırakılmıştır.

---

## Signal & UI Senkronizasyon Mimarisi

Tüm veri değişimleri (ekle/düzenle/sil/tamamla) `data_changed = pyqtSignal()` üzerinden iletilir:

```
MainWindow.data_changed ──┐
                          ├──► refresh_all() in main.py
DesktopWidget.data_changed┘         │
                                    ├── window.refresh()
                                    └── widget.refresh()
```

- `ReminderEngine.task_notified` da `refresh_all()`'a bağlıdır.
- `TaskListWidget` ve `WidgetTabView` sinyalleri `Task` nesnesi taşır (int task_id değil).
  Bu sayede virtual occurrence'ların `due_date`'i signal zinciri boyunca korunur.

---

## Tekrarlayan Görev Mimarisi

Tekrarlayan görevler veritabanında tek bir **seed task** satırı olarak tutulur. Occurrence'lar DB'de saklanmaz; her sorguda `task_service._occurrences_in_range()` tarafından üretilir:

```python
for base in repository.get_recurring_tasks():
    rule = repository.get_recurrence_rule(base.recurrence_id)
    effective_start = max(start, base.due_date)   # seri öncesi occurrence engeli
    for occ_date in recurrence_service.generate_occurrences(rule, effective_start, end):
        virtual = copy.copy(base)
        virtual.due_date = occ_date               # id = seed id, due_date = occurrence tarihi
        result.append(virtual)
```

**İstisna yönetimi:**
- "Sadece bu instance'ı sil" → `task_exceptions` tablosuna `is_deleted=True` kaydı; seed korunur.
- "Sadece bu instance'ı düzenle" → Yeni standalone task oluşturulur + `task_exceptions` tablosuna `modified_task_id` kaydı; seed korunur. Occurrence generator bu tarihi atlar.

---

## Bildirim Motoru

`ReminderEngine` arka planda bir `QTimer` ile her dakika çalışır:

- Bugün ve son 30 gündeki görevler sorgulanır (gecikmiş görevler için lookback).
- `NotificationService.send_toast()` ile Windows Toast bildirimi gönderilir.
- Aynı görev için aynı gün birden fazla bildirim gönderilmez.
- Bildirim öncesi süre `config` üzerinden ayarlanabilir (varsayılan: 15 dk).

---

## Modüler Genişleme Kapıları

- `plugins/` klasörü eklenerek yeni modüller entegre edilebilir.
- `ReminderEngine` yeni trigger tipleri destekleyebilir (konum, uygulama açılışı).
- `NotificationService` farklı kanallarla (e-posta, ses) genişletilebilir.
- Tema sistemi `dark_theme.qss` yanına yeni `.qss` dosyaları eklenerek büyütülebilir.
