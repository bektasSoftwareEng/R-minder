# R-minder — Geliştirme Yol Haritası

## Faz 1 — Temel Altyapı (Core)

### 1.1 Proje İskeleti
- [x] Klasör yapısı ve `__init__.py` dosyaları
- [x] `requirements.txt` oluşturma (PyQt6, winotify)
- [x] `main.py` entry point

### 1.2 Veri Katmanı
- [x] `database.py` — SQLite bağlantı ve migration sistemi
- [x] `models.py` — Task, RecurrenceRule, TaskException dataclass'ları
- [x] `repository.py` — CRUD operasyonları (oluştur, oku, güncelle, sil)

### 1.3 Servis Katmanı (Temel)
- [x] `task_service.py` — görev iş mantığı, öncelik hesaplama
- [x] `recurrence_service.py` — basit tekrarlama (günlük, haftalık, aylık, yıllık)
- [x] `config.py` — ayar okuma/yazma (widget konumu vb.)

---

## Faz 2 — Ana Pencere (Main Window)

### 2.1 Ana Pencere İskeleti
- [x] `main_window.py` — PyQt6 ana pencere, menü çubuğu
- [x] System tray entegrasyonu (`system_tray.py`)
- [x] Minimize to tray davranışı

### 2.2 Görev Yönetimi UI
- [x] `task_list.py` — görev listesi (filtreleme, sıralama)
- [x] `task_form.py` — görev ekleme/düzenleme formu
- [x] `recurrence_picker.py` — tekrarlama pattern seçici

### 2.3 Koyu Tema
- [x] `dark_theme.qss` — tam koyu tema stylesheet
- [x] `colors.py` — öncelik renk sabitleri

---

## Faz 3 — Masaüstü Widget

### 3.1 Widget Altyapısı
- [x] Frameless + şeffaf arka planlı widget penceresi (`WindowStaysOnBottomHint`)
- [x] Daralt / Genişlet (collapse/expand) toggle
- [x] `embedder.py` — Win32 Progman/WorkerW kodu (Windows 11 uyumsuzluğu nedeniyle pasif)

### 3.2 Widget UI
- [x] `tab_view.py` — Bugün / Yarın / Bu Hafta sekmeleri
- [x] `task_card.py` — görev kartı bileşeni (renk, öncelik göstergesi)
- [x] Widget üzerinden hızlı tamamla / sil
- [x] Widget üzerinden hızlı görev ekleme

### 3.3 Widget Etkileşim
- [x] Sürükle-bırak ile konum değiştirme
- [x] Köşelerden boyutlandırma (QSizeGrip)
- [x] Konum/boyut ayarlarını kaydetme

---

## Faz 4 — Bildirim & Zamanlama Motoru

### 4.1 Arka Plan Motoru
- [x] `reminder_engine.py` — QTimer tabanlı arka plan kontrol döngüsü
- [x] Yaklaşan görev tespiti (varsayılan: 15 dk önce)
- [x] Tekrar bildirim gönderme koruması (aynı gün aynı göreve bir kez)
- [x] 30 günlük lookback — geçmiş gecikmiş görevler de yakalanır

### 4.2 Windows Toast Bildirimleri
- [x] `notification_service.py` — winotify entegrasyonu
- [x] Bildirim öncesi süreyi ayarlar üzerinden değiştirme

---

## Faz 5 — Gelişmiş Tekrarlama

### 5.1 Özel Tekrarlama Kuralları
- [x] "Her ayın Nth günü" desteği
- [x] "Her N haftada bir" desteği
- [x] "Belirli haftanın günleri" (Pazartesi + Çarşamba gibi)

### 5.2 İstisna Yönetimi
- [x] "Sadece bu instance'ı düzenle" — yeni bağımsız task oluşturur, seed'e dokunmaz
- [x] "Bu instance'ı sil, diğerleri devam etsin" — sadece exception kaydı, seed korunur
- [x] `task_exceptions` tablosu entegrasyonu
- [x] Virtual occurrence üretimi — tekrarlayan görevler query-time'da üretilir, DB'de saklanmaz

---

## Faz 6 — Cilalama & Dağıtım

### 6.1 UX İyileştirmeleri
- [x] Saat alanı toggle (sadece saat gerekliyse görünür)
- [x] ClickFocus politikası — alan seçilmeden cursor girmez
- [x] Spinner/DateEdit butonlarında pointer cursor
- [ ] Animasyonlar (kart geçişleri, sekme değişimi)
- [ ] Klavye kısayolları
- [ ] Widget sağ tık context menüsü

### 6.2 Ayarlar Ekranı
- [x] `settings_dialog.py` — bildirim öncesi süre, widget konum sıfırlama, autostart
- [x] Widget konumunu sıfırlama (kayıtlı geometriyi uygular, widget'ı gösterir)
- [x] Windows başlangıcında otomatik başlatma (registry)

### 6.3 Paketleme
- [ ] PyInstaller ile tek `.exe` üretimi
- [ ] İkon ve assets gömme
- [ ] Kurulum testi

---

## Gelecek (Faz 7+) — Opsiyonel Genişlemeler

- Tema seçici (açık / koyu / özel)
- Görev kategorileri / etiketler
- İstatistik ekranı (tamamlanan görevler, gecikmeler)
- Veri yedekleme / dışa aktarma (JSON/CSV)
- Plugin sistemi
- Çoklu dil desteği
