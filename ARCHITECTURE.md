# R-minder — Sistem Mimarisi

## Genel Bakış

R-minder, Windows masaüstüne gömülü bir widget ve tam özellikli bir ana pencereden oluşan, modüler yapıda geliştirilmiş bir hatırlatıcı masaüstü uygulamasıdır.

**Teknoloji Yığını:**
- Python 3.11+
- PyQt6 (UI framework)
- SQLite (veri depolama)
- ctypes / Win32 API (masaüstü widget gömme)
- winotify (Windows Toast bildirimleri)

---

## Katman Yapısı

```
┌─────────────────────────────────────────────────────┐
│                    UI LAYER                          │
│  ┌─────────────────┐    ┌──────────────────────┐    │
│  │  Desktop Widget │    │    Main Window        │    │
│  │  (Progman embed)│    │  (System Tray → App)  │    │
│  │  Today/Tomorrow │    │  Full CRUD + Settings │    │
│  │  /This Week tabs│    │                       │    │
│  └────────┬────────┘    └──────────┬────────────┘   │
└───────────┼─────────────────────────┼───────────────┘
            │    PyQt6 Signals/Slots   │
┌───────────▼─────────────────────────▼───────────────┐
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
│   │   ├── models.py                # Task, RecurrenceRule dataclass'ları
│   │   └── repository.py           # Tüm CRUD operasyonları
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py          # İş mantığı, öncelik hesaplama
│   │   ├── recurrence_service.py    # Tekrarlama genişletme ve çözme
│   │   ├── notification_service.py  # Windows Toast bildirimleri
│   │   └── reminder_engine.py       # Arka plan thread, zamanlayıcı
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── widget/
│   │   │   ├── __init__.py
│   │   │   ├── desktop_widget.py    # Ana widget penceresi
│   │   │   ├── embedder.py          # Win32/ctypes Progman masaüstü gömme
│   │   │   ├── task_card.py         # Tekil görev bileşeni
│   │   │   └── tab_view.py          # Bugün / Yarın / Bu Hafta sekmeleri
│   │   ├── main_window/
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py       # Ana uygulama penceresi
│   │   │   ├── task_form.py         # Ekle / Düzenle formu
│   │   │   ├── task_list.py         # Tam görev listesi görünümü
│   │   │   └── recurrence_picker.py # Tekrarlama pattern seçici UI
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
-- Ana görev tablosu
CREATE TABLE tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    description     TEXT,
    due_date        DATE NOT NULL,
    due_time        TIME,                    -- NULL ise sadece tarih bazlı
    is_completed    BOOLEAN DEFAULT 0,
    completed_at    DATETIME,
    recurrence_id   INTEGER REFERENCES recurrence_rules(id),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tekrarlama kuralları
CREATE TABLE recurrence_rules (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type       TEXT NOT NULL,           -- 'daily','weekly','monthly','yearly','custom'
    interval        INTEGER DEFAULT 1,       -- her N günde/haftada/ayda
    day_of_week     TEXT,                    -- haftalık: 'MON,WED,FRI'
    day_of_month    INTEGER,                 -- aylık: ayın kaçında (1-31)
    month_of_year   INTEGER,                 -- yıllık: hangi ay
    end_date        DATE,                    -- opsiyonel bitiş tarihi
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tekrarlayan görev istisnaları
-- "Sadece bu ay'ı değiştir" veya "bu instance'ı sil" için
CREATE TABLE task_exceptions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    recurrence_id    INTEGER NOT NULL REFERENCES recurrence_rules(id),
    original_date    DATE NOT NULL,          -- hangi instance etkilendi
    modified_task_id INTEGER REFERENCES tasks(id),  -- değiştirilmiş versiyon
    is_deleted       BOOLEAN DEFAULT 0,      -- bu instance tamamen silindi mi
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Uygulama ayarları (key-value store)
CREATE TABLE settings (
    key     TEXT PRIMARY KEY,
    value   TEXT
);
-- Örnek kayıtlar:
-- widget_x, widget_y, widget_width, widget_height
-- notification_lead_minutes (kaç dakika önce bildirim)
-- theme, language
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

## Widget — Masaüstü Gömme Mekanizması

Windows'ta pencereyi masaüstü shell'ine gömmek için `Progman/WorkerW` yöntemi kullanılır:

1. `Progman` penceresi bulunur.
2. `0x052C` mesajı gönderilerek `WorkerW` katmanı oluşturulur.
3. Widget penceresi `WorkerW`'nin child'ı yapılır.
4. Explorer yeniden başlarsa `embedder.py` içindeki watchdog otomatik yeniden gömer.

Bu mantık tamamen `app/ui/widget/embedder.py` içinde izole edilmiştir — diğer modüller bu detayı bilmez.

---

## Bildirim Motoru

`ReminderEngine` arka planda bir `QTimer` ile her dakika çalışır:

- Saati yaklaşan görevler tespit edilir (varsayılan: 15 dk önce uyarı).
- `NotificationService.send_toast()` ile Windows Toast bildirimi gönderilir.
- Aynı görev için aynı gün birden fazla bildirim gönderilmez (gönderildi kaydı tutulur).

---

## Modüler Genişleme Kapıları

Uygulama ileride şu şekillerde genişletilebilir:

- `plugins/` klasörü eklenerek yeni modüller entegre edilebilir.
- `ReminderEngine` yeni trigger tipleri destekleyebilir (konum, uygulama açılışı).
- `NotificationService` farklı kanallarla (e-posta, ses) genişletilebilir.
- Tema sistemi `dark_theme.qss` yanına yeni `.qss` dosyaları eklenerek büyütülebilir.
- Dil desteği `settings` tablosu üzerinden yönetilebilir.
