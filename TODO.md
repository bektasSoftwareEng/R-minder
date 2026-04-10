# R-minder — Aktif Görev Listesi

> Şu an üzerinde çalışılan faz: **Faz 5 — Gelişmiş Tekrarlama İstisnaları**

---

## Yapılacaklar

### Faz 5.1 — İstisna Yönetimi UI
- [ ] "Sadece bu instance'ı düzenle" dialog akışı
- [ ] "Bu instance'ı sil, diğerleri devam etsin" akışı
- [ ] `task_exceptions` tablosu UI entegrasyonu

### Faz 5.2 — Recurrence Edge Cases
- [ ] "Her ayın Nth günü" desteği
- [ ] recurrence_service istisna senaryoları

### Faz 3.1 — Widget Altyapısı
- [x] `app/ui/widget/embedder.py` — Progman/WorkerW Win32 gömme + watchdog
- [x] Explorer yeniden başlatma watchdog (5sn kontrol)
- [x] Frameless + şeffaf arka planlı widget penceresi

### Faz 3.2 — Widget UI
- [x] `app/ui/widget/tab_view.py` — Bugün / Yarın / Bu Hafta sekmeleri
- [x] `app/ui/widget/task_card.py` — kompakt görev kartı
- [x] Hızlı tamamla / sil butonları

### Faz 3.3 — Widget Etkileşim
- [x] Başlık çubuğundan sürükle-bırak konum değiştirme
- [x] QSizeGrip ile köşeden boyutlandırma
- [x] Konum/boyut kaydetme (config'e)

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

### Faz 2.1 — Ana Pencere İskeleti
- [x] `app/ui/main_window/main_window.py` — PyQt6 ana pencere
- [x] `app/ui/system_tray.py` — System tray ikonu ve menüsü
- [x] Minimize to tray davranışı

### Faz 2.2 — Görev Yönetimi UI
- [x] `app/ui/main_window/task_list.py` — görev listesi (TaskCard + TaskListWidget)
- [x] `app/ui/main_window/task_form.py` — ekle/düzenle formu
- [x] `app/ui/main_window/recurrence_picker.py` — tekrarlama seçici

### Faz 2.3 — Koyu Tema
- [x] `app/ui/styles/dark_theme.qss`
- [x] `app/ui/styles/colors.py`

### Faz 4.1 — Arka Plan Motoru
- [x] `app/services/reminder_engine.py` — QTimer tabanlı arka plan kontrol döngüsü
- [x] Yaklaşan görev tespiti (varsayılan: 15 dk önce)
- [x] Tekrar bildirim gönderme koruması (aynı gün aynı göreve bir kez)
- [x] Geçmiş tarihlerdeki gecikmiş görevler 30 günlük lookback ile yakalanıyor
- [x] Dakika yuvarlama düzeltmesi (round yerine int)

### Faz 4.2 — Windows Toast Bildirimleri
- [x] `app/services/notification_service.py` — winotify entegrasyonu
- [x] Bildirim öncesi süreyi config üzerinden ayarlama

---

## Notlar

- Faz 1 tamamlanmadan UI'a geçilmeyecek — veri katmanı sağlam olmalı.
- Her faz tamamlandıkça bu dosya ve `ROADMAP.md` güncellenecek.
- Mimari kararlar için `ARCHITECTURE.md`'e bakılacak.
