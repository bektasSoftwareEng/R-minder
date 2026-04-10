# R-minder — Aktif Görev Listesi

> Şu an üzerinde çalışılan faz: **Faz 6.3 — PyInstaller Paketleme**

---

## Yapılacaklar

### Faz 6.3 — Paketleme
- [ ] PyInstaller ile tek `.exe` üretimi
- [ ] İkon ve assets gömme
- [ ] Kurulum testi (temiz Windows ortamında)

### Faz 6.1 — Kalan UX İyileştirmeleri
- [ ] Animasyonlar (kart geçişleri, sekme değişimi)
- [ ] Klavye kısayolları
- [ ] Widget sağ tık context menüsü

---

## Tamamlananlar

### Faz 1.1 — Proje İskeleti
- [x] Klasör yapısı ve `__init__.py` dosyaları
- [x] `requirements.txt` (PyQt6, winotify)
- [x] `main.py` entry point

### Faz 1.2 — Veri Katmanı
- [x] `app/core/database.py` — bağlantı, tablo oluşturma, migration
- [x] `app/core/models.py` — Task, RecurrenceRule, TaskException dataclass'ları
- [x] `app/core/repository.py` — CRUD operasyonları + `get_recurring_tasks`, `update_recurrence_rule`

### Faz 1.3 — Servis Katmanı
- [x] `app/services/task_service.py` — öncelik hesaplama, `_occurrences_in_range`, `_non_recurring_in_range`
- [x] `app/services/recurrence_service.py` — tekrarlama üretici, `create_exception_delete`, `create_exception_modify`
- [x] `app/utils/config.py` — ayar okuma/yazma
- [x] `app/utils/date_utils.py` — tarih yardımcıları
- [x] `app/utils/priority.py` — aciliyet renk ve sıra hesaplama

### Faz 2.1 — Ana Pencere İskeleti
- [x] `app/ui/main_window/main_window.py` — PyQt6 ana pencere
- [x] `app/ui/system_tray.py` — System tray ikonu ve menüsü
- [x] Minimize to tray davranışı

### Faz 2.2 — Görev Yönetimi UI
- [x] `app/ui/main_window/task_list.py` — görev listesi (TaskCard + TaskListWidget)
- [x] `app/ui/main_window/task_form.py` — ekle/düzenle formu, saat toggle, ClickFocus
- [x] `app/ui/main_window/recurrence_picker.py` — tekrarlama seçici
- [x] `app/ui/main_window/recurrence_action_dialog.py` — "sadece bu / tüm seri" dialog

### Faz 2.3 — Koyu Tema
- [x] `app/ui/styles/dark_theme.qss` — pointer cursor, spinner buton hover stilleri dahil
- [x] `app/ui/styles/colors.py`

### Faz 3.1-3.3 — Masaüstü Widget
- [x] `app/ui/widget/desktop_widget.py` — WindowStaysOnBottomHint floating window, collapse/expand
- [x] `app/ui/widget/tab_view.py` — Bugün / Yarın / Bu Hafta sekmeleri
- [x] `app/ui/widget/task_card.py` — kompakt görev kartı
- [x] Sürükle-bırak, QSizeGrip, konum/boyut kaydetme

### Faz 4 — Bildirim & Zamanlama Motoru
- [x] `app/services/reminder_engine.py` — 30 günlük lookback, round() düzeltmesi
- [x] `app/services/notification_service.py` — winotify, bildirim öncesi süre config'den

### Faz 5 — Gelişmiş Tekrarlama İstisnaları
- [x] Virtual occurrence üretimi — `_occurrences_in_range` ile query-time üretim
- [x] `effective_start = max(start, base.due_date)` — seri öncesi occurrence engeli
- [x] Recurring tasklar tarih sekmelerinde gösteriliyor (Bugün/Yarın/Bu Hafta)
- [x] "Sadece bu instance'ı düzenle" — yeni standalone task + exception modify, seed korunur
- [x] "Bu instance'ı sil" — exception delete kaydı, seed korunur
- [x] Widget üzerinden recurring task silme de exception tabanlı

### Faz 6.1-6.2 — UX & Ayarlar
- [x] `app/ui/settings_dialog.py` — bildirim süresi, widget konum sıfırlama, Windows autostart
- [x] `widget_reset_requested` sinyali — ayarlardan sıfırlama widget'ı doğru konuma taşır
- [x] Signal mimarisi yeniden yazıldı — `data_changed` + `Task` object sinyalleri
- [x] Saat alanı toggle (sadece aktifken görünür)
- [x] ClickFocus politikası tüm input alanlarında

---

## Notlar

- Mimari kararlar için `ARCHITECTURE.md`'e bakılacak.
- Her faz tamamlandıkça bu dosya ve `ROADMAP.md` güncellenecek.
- Codex review → merge → push sırası: feature branch'te /codex:review, onaylandıktan sonra merge, push yalnızca kullanıcı istediğinde.
