# R-minder

Windows masaüstünde her zaman görünür, koyu temalı bir hatırlatıcı uygulaması.

Widget masaüstünde floating olarak durur — üstüne bir pencere açılmadığı sürece her zaman görünür. Masaüstüne döndüğünde yapılacakların orada seni bekler.

---

## Özellikler

- **Masaüstü Widget** — her zaman altta kalan floating panel; daraltılıp genişletilebilir
- **Bugün / Yarın / Bu Hafta** sekmeleri — hem widget'ta hem ana pencerede
- **Öncelik Sistemi** — saate yaklaştıkça renk değişir, görev üste çıkar
  - Gecikmiş → Kırmızı
  - < 2 saat → Turuncu
  - 2–24 saat → Sarı
  - Bugün (saatsiz) → Mavi
- **Tekrarlayan Görevler** — günlük, haftalık (belirli günler), aylık, yıllık, özel aralık
- **Instance Yönetimi** — tekrarlayan görevin sadece bir kopyasını düzenle veya sil; seri bozulmaz
- **Windows Toast Bildirimleri** — görev zamanı yaklaşınca uyarı
- **Ayarlar Ekranı** — bildirim süresi, widget konum sıfırlama, Windows otomatik başlatma
- **System Tray** — arka planda çalışır, tray'den açılır
- **Koyu Tema** — Catppuccin Mocha bazlı, göz yormayan

---

## Gereksinimler

- Windows 10 / 11
- Python 3.11+ (**sistem Python — Anaconda değil**)

> **Not:** Anaconda ortamında PyQt6 DLL yükleme hatası alınabilir.
> Sistem Python'ını kullan: `C:\Users\<kullanıcı>\AppData\Local\Programs\Python\Python3xx\`

---

## Kurulum

```bash
git clone https://github.com/bektasSoftwareEng/R-minder.git
cd R-minder
pip install -r requirements.txt
python main.py
```

İlk çalıştırmada `data/rminder.db` dosyası otomatik oluşturulur.

---

## Kullanım

### Widget
- Masaüstünde otomatik belirir — floating, her zaman altta kalır
- **Başlık çubuğunu sürükle** → widget'ı taşı
- **Sağ alt köşeyi sürükle** → boyutlandır
- **`▲/▼` butonu** → widget'ı daralt / genişlet
- **`+` butonu** → hızlı görev ekle (ana pencere açılır)
- **`⊞` butonu** → ana pencereyi aç/kapat
- **`✓`** → görevi tamamlandı işaretle
- **`✕`** → görevi sil

### Ana Pencere
- System tray ikonuna **çift tıkla** veya sağ tık → Göster
- **`+ Yeni Görev`** butonu → görev ekle
- Görev kartındaki **`✎`** → düzenle, **`✕`** → sil
- **`⊞ Widget`** butonu → widget'ı göster/gizle
- **`⚙`** butonu → ayarlar
- Pencereyi kapatmak → system tray'e küçülür, uygulama çalışmaya devam eder

### Tekrarlayan Görev Eklemek
1. Yeni Görev formunu aç
2. "Tekrar" bölümünden tip seç (Günlük / Haftalık / Aylık / Yıllık / Özel)
3. Aralık ve bitiş tarihi ayarla (opsiyonel)
4. Haftalık seçildiyse hangi günler tekrarlayacağını işaretle

### Tekrarlayan Görev Düzenlemek / Silmek
- Düzenle veya sil butonuna basınca "Sadece bu / Tüm seri" seçeneği çıkar
- **Sadece bu:** Bu occurrence için yeni bağımsız görev oluşturulur; serinin geri kalanı bozulmaz
- **Tüm seri:** Kural ve tüm gelecek occurrencelar etkilenir

---

## Proje Yapısı

```
R-minder/
├── main.py                          # Giriş noktası
├── app/
│   ├── core/
│   │   ├── database.py              # SQLite bağlantı ve migration
│   │   ├── models.py                # Veri modelleri (Task, RecurrenceRule, TaskException)
│   │   └── repository.py           # CRUD operasyonları
│   ├── services/
│   │   ├── task_service.py          # İş mantığı, öncelik, occurrence üretimi
│   │   ├── recurrence_service.py    # Tekrarlama üretici ve istisna yönetimi
│   │   ├── notification_service.py  # Windows Toast bildirimleri
│   │   └── reminder_engine.py       # Arka plan zamanlayıcı
│   ├── ui/
│   │   ├── widget/
│   │   │   ├── desktop_widget.py    # Floating widget (WindowStaysOnBottomHint)
│   │   │   ├── task_card.py         # Kompakt görev kartı
│   │   │   └── tab_view.py          # Bugün/Yarın/Bu Hafta sekmeleri
│   │   ├── main_window/
│   │   │   ├── main_window.py       # Ana uygulama penceresi
│   │   │   ├── task_form.py         # Ekle/Düzenle diyalogu
│   │   │   ├── task_list.py         # Görev listesi (TaskCard + TaskListWidget)
│   │   │   ├── recurrence_picker.py # Tekrarlama pattern seçici
│   │   │   └── recurrence_action_dialog.py  # "Sadece bu / Tüm seri" dialogu
│   │   ├── settings_dialog.py       # Ayarlar ekranı
│   │   ├── system_tray.py           # System tray ikonu ve menüsü
│   │   └── styles/
│   │       ├── dark_theme.qss       # Koyu tema (Catppuccin Mocha bazlı)
│   │       └── colors.py            # Öncelik renk sabitleri
│   └── utils/
│       ├── config.py                # DB üzerinden ayar okuma/yazma
│       ├── date_utils.py            # Bugün/Yarın/Bu Hafta hesaplama
│       └── priority.py              # 5 seviyeli aciliyet hesaplama
├── data/                            # SQLite veritabanı (git'e dahil değil)
├── assets/                          # İkonlar (gelecek faz)
├── ARCHITECTURE.md                  # Sistem mimarisi ve kararlar
├── ROADMAP.md                       # Geliştirme yol haritası
└── TODO.md                          # Aktif görev listesi
```

---

## Veritabanı

Uygulama `data/rminder.db` adında bir SQLite dosyası oluşturur. Bu dosya repoya dahil değildir (`.gitignore`). Yedeklemek istersen bu dosyayı kopyalamak yeterlidir.

---

## Geliştirme Fazları

| Faz | Konu | Durum |
|-----|------|-------|
| 1 | Temel altyapı — DB, modeller, servisler | ✅ Tamamlandı |
| 2 | Ana pencere, system tray, koyu tema | ✅ Tamamlandı |
| 3 | Masaüstü widget, daralt/genişlet | ✅ Tamamlandı |
| 4 | Bildirim motoru (Windows Toast) | ✅ Tamamlandı |
| 5 | Gelişmiş tekrarlama istisnaları | ✅ Tamamlandı |
| 6A | Ayarlar ekranı, UX iyileştirmeleri | ✅ Tamamlandı |
| 6B | Paketleme (.exe) | ⏳ Sırada |

Detaylar için [ROADMAP.md](ROADMAP.md) ve [ARCHITECTURE.md](ARCHITECTURE.md) dosyalarına bak.

---

## Mimari Notlar

- **Katmanlar birbirinden bağımsız:** `core/` UI bilmez, `services/` DB'ye doğrudan erişmez, `ui/` sadece servisleri çağırır.
- **Senkronizasyon:** Tüm veri değişimleri `data_changed` sinyali üzerinden `refresh_all()`'a iletilir; hem ana pencere hem widget aynı anda güncellenir.
- **Tekrarlayan görevler:** DB'de tek seed satırı tutulur; occurrence'lar her sorguda query-time üretilir. İstisnalar `task_exceptions` tablosuna kaydedilir.
- **Widget konumlandırma:** `WindowStaysOnBottomHint` ile her zaman altta kalan floating window. Win32 Progman gömme Windows 11'de çalışmadığı için tercih edilmedi.
- **Öncelik hesaplama:** Veritabanında saklanmaz, `task_service` her sorguda anlık hesaplar.
