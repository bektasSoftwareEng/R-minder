# R-minder — Aktif Görev Listesi

> Şu an üzerinde çalışılan faz: **Faz 2 — Ana Pencere**

---

## Yapılacaklar

### Faz 2.1 — Ana Pencere İskeleti
- [ ] `app/ui/main_window/main_window.py` — PyQt6 ana pencere
- [ ] `app/ui/system_tray.py` — System tray ikonu ve menüsü
- [ ] Minimize to tray davranışı

### Faz 2.2 — Görev Yönetimi UI
- [ ] `app/ui/main_window/task_list.py` — görev listesi
- [ ] `app/ui/main_window/task_form.py` — ekle/düzenle formu
- [ ] `app/ui/main_window/recurrence_picker.py` — tekrarlama seçici

### Faz 2.3 — Koyu Tema
- [ ] `app/ui/styles/dark_theme.qss`
- [ ] `app/ui/styles/colors.py`

---

## Tamamlananlar

### Faz 1.1 — Proje İskeleti
- [x] Klasör yapısı ve `__init__.py` dosyaları
- [x] `requirements.txt` (PyQt6, winotify)
- [x] `main.py` entry point

### Faz 1.2 — Veri Katmanı
- [x] `app/core/database.py` — bağlantı, tablo oluşturma, migration
- [x] `app/core/models.py` — Task, RecurrenceRule, TaskException dataclass'ları
- [x] `app/core/repository.py` — CRUD operasyonları

### Faz 1.3 — Servis Katmanı
- [x] `app/services/task_service.py` — öncelik hesaplama, görev sıralama
- [x] `app/services/recurrence_service.py` — tekrarlama mantığı
- [x] `app/utils/config.py` — ayar okuma/yazma
- [x] `app/utils/date_utils.py` — tarih yardımcıları
- [x] `app/utils/priority.py` — aciliyet renk ve sıra hesaplama

---

## Notlar

- Faz 1 tamamlanmadan UI'a geçilmeyecek — veri katmanı sağlam olmalı.
- Her faz tamamlandıkça bu dosya ve `ROADMAP.md` güncellenecek.
- Mimari kararlar için `ARCHITECTURE.md`'e bakılacak.
