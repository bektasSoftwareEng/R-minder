# R-minder — Geliştirme Yol Haritası

## Faz 1 — Temel Altyapı (Core)

Uygulamanın çalışması için gereken minimum yapı.

### 1.1 Proje İskeleti
- [ ] Klasör yapısı ve `__init__.py` dosyaları
- [ ] `requirements.txt` oluşturma (PyQt6, winotify)
- [ ] `main.py` entry point

### 1.2 Veri Katmanı
- [ ] `database.py` — SQLite bağlantı ve migration sistemi
- [ ] `models.py` — Task, RecurrenceRule, TaskException dataclass'ları
- [ ] `repository.py` — CRUD operasyonları (oluştur, oku, güncelle, sil)

### 1.3 Servis Katmanı (Temel)
- [ ] `task_service.py` — görev iş mantığı, öncelik hesaplama
- [ ] `recurrence_service.py` — basit tekrarlama (günlük, haftalık, aylık, yıllık)
- [ ] `config.py` — ayar okuma/yazma (widget konumu vb.)

---

## Faz 2 — Ana Pencere (Main Window)

Tam özellikli yönetim arayüzü.

### 2.1 Ana Pencere İskeleti
- [ ] `main_window.py` — PyQt6 ana pencere, menü çubuğu
- [ ] System tray entegrasyonu (`system_tray.py`)
- [ ] Minimize to tray davranışı

### 2.2 Görev Yönetimi UI
- [ ] `task_list.py` — görev listesi (filtreleme, sıralama)
- [ ] `task_form.py` — görev ekleme/düzenleme formu
- [ ] `recurrence_picker.py` — tekrarlama pattern seçici

### 2.3 Koyu Tema
- [ ] `dark_theme.qss` — tam koyu tema stylesheet
- [ ] `colors.py` — öncelik renk sabitleri

---

## Faz 3 — Masaüstü Widget

Masaüstüne gömülü her zaman görünen panel.

### 3.1 Widget Altyapısı
- [ ] `embedder.py` — Progman/WorkerW Win32 gömme mekanizması
- [ ] Explorer yeniden başlatma watchdog
- [ ] Widget pencere çerçevesi (frameless, şeffaf arka plan)

### 3.2 Widget UI
- [ ] `tab_view.py` — Bugün / Yarın / Bu Hafta sekmeleri
- [ ] `task_card.py` — görev kartı bileşeni (renk, öncelik göstergesi)
- [ ] Widget üzerinden hızlı tamamla / sil
- [ ] Widget üzerinden hızlı görev ekleme

### 3.3 Widget Etkileşim
- [ ] Sürükle-bırak ile konum değiştirme
- [ ] Köşelerden boyutlandırma
- [ ] Konum/boyut ayarlarını kaydetme

---

## Faz 4 — Bildirim & Zamanlama Motoru

### 4.1 Arka Plan Motoru
- [ ] `reminder_engine.py` — QTimer tabanlı arka plan kontrol döngüsü
- [ ] Yaklaşan görev tespiti (varsayılan: 15 dk önce)
- [ ] Tekrar bildirim gönderme koruması

### 4.2 Windows Toast Bildirimleri
- [ ] `notification_service.py` — winotify entegrasyonu
- [ ] Bildirime tıklayınca göreve gitme
- [ ] Bildirim öncesi süreyi ayarlar üzerinden değiştirme

---

## Faz 5 — Gelişmiş Tekrarlama

### 5.1 Özel Tekrarlama Kuralları
- [ ] "Her ayın Nth günü" desteği
- [ ] "Her N haftada bir" desteği
- [ ] "Belirli haftanın günleri" (Pazartesi + Çarşamba gibi)

### 5.2 İstisna Yönetimi
- [ ] "Sadece bu instance'ı düzenle" (tek seferlik override)
- [ ] "Bu instance'ı sil, diğerleri devam etsin"
- [ ] `task_exceptions` tablosu entegrasyonu

---

## Faz 6 — Cilalama & Dağıtım

### 6.1 UX İyileştirmeleri
- [ ] Animasyonlar (kart geçişleri, sekme değişimi)
- [ ] Klavye kısayolları
- [ ] Widget sağ tık context menüsü

### 6.2 Ayarlar Ekranı
- [ ] Bildirim öncesi süre
- [ ] Widget varsayılan konum/boyut sıfırlama
- [ ] Başlangıçta otomatik başlatma (Windows startup registry)

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
