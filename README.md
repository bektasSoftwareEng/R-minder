# R-minder

Windows masaüstüne gömülü, her zaman görünür bir hatırlatıcı uygulaması.

Widget duvar kağıdının önünde, masaüstü ikonlarının arkasında sabitlenir — masaüstüne her döndüğünde yapılacakları görürsün.

---

## Özellikler

- **Masaüstü Widget** — Progman/WorkerW Win32 gömme; ikonların arkasında, her zaman görünür
- **Bugün / Yarın / Bu Hafta** sekmeleri — hem widget'ta hem ana pencerede
- **Öncelik Sistemi** — saate yaklaştıkça renk değişir, görev üste çıkar
  - Gecikmiş → Kırmızı
  - < 2 saat → Turuncu
  - 2–24 saat → Sarı
  - Bugün (saatsiz) → Mavi
- **Tekrarlayan Görevler** — günlük, haftalık (belirli günler), aylık, yıllık, özel aralık
- **Instance Düzenleme** — tekrarlayan görevin sadece bir kopyasını değiştir
- **Windows Toast Bildirimleri** — görev zamanı yaklaşınca uyarı *(Faz 4)*
- **System Tray** — arka planda çalışır, tray'den açılır
- **Koyu Tema** — varsayılan, göz yormayan
- **Sürüklenebilir & Boyutlandırılabilir Widget** — konum ve boyut kaydedilir

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
- Masaüstünde otomatik belirir — ikonların arkasında, duvar kağıdının önünde
- **Başlık çubuğunu sürükle** → widget'ı taşı
- **Sağ alt köşeyi sürükle** → boyutlandır
- **`+` butonu** → hızlı görev ekle (ana pencere açılır)
- **`⊞` butonu** → ana pencereyi aç/kapat
- **`✓`** → görevi tamamlandı işaretle
- **`✕`** → görevi sil

### Ana Pencere
- System tray ikonuna **çift tıkla** veya sağ tık → Göster
- **`+ Yeni Görev`** butonu → görev ekle
- Görev kartındaki **`✎`** → düzenle, **`✕`** → sil
- Pencereyi kapatmak → system tray'e küçülür, uygulama çalışmaya devam eder

### Tekrarlayan Görev Eklemek
1. Yeni Görev formunu aç
2. "Tekrar" bölümünden tip seç (Günlük / Haftalık / Aylık / Yıllık / Özel)
3. Aralık ve bitiş tarihi ayarla (opsiyonel)
4. Haftalık seçildiyse hangi günler tekrarlayacağını işaretle

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
│   │   ├── task_service.py          # İş mantığı, öncelik hesaplama, sıralama
│   │   ├── recurrence_service.py    # Tekrarlama üretici ve istisna yönetimi
│   │   ├── notification_service.py  # Windows Toast bildirimleri  [Faz 4]
│   │   └── reminder_engine.py       # Arka plan zamanlayıcı       [Faz 4]
│   ├── ui/
│   │   ├── widget/
│   │   │   ├── desktop_widget.py    # Ana widget penceresi (frameless, şeffaf)
│   │   │   ├── embedder.py          # Win32 Progman/WorkerW gömme + watchdog
│   │   │   ├── task_card.py         # Kompakt görev kartı
│   │   │   └── tab_view.py          # Bugün/Yarın/Bu Hafta sekmeleri
│   │   ├── main_window/
│   │   │   ├── main_window.py       # Ana uygulama penceresi
│   │   │   ├── task_form.py         # Ekle/Düzenle diyalogu
│   │   │   ├── task_list.py         # Görev listesi (TaskCard + TaskListWidget)
│   │   │   └── recurrence_picker.py # Tekrarlama pattern seçici
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
| 3 | Masaüstü widget, Win32 gömme | ✅ Tamamlandı |
| 4 | Bildirim motoru (Windows Toast) | ✅ Tamamlandı |
| 5 | Gelişmiş tekrarlama istisnaları | ⏳ Bekliyor |
| 6 | Paketleme (.exe), ayarlar ekranı | ⏳ Bekliyor |

Detaylar için [ROADMAP.md](ROADMAP.md) ve [ARCHITECTURE.md](ARCHITECTURE.md) dosyalarına bak.

---

## Mimari Notlar

- **Katmanlar birbirinden bağımsız:** `core/` UI bilmez, `services/` DB'ye doğrudan erişmez, `ui/` sadece servisleri çağırır.
- **Modüler:** `plugins/` klasörü ile ileride yeni modüller eklenebilir.
- **Widget gömme:** Progman'a `0x052C` mesajı → WorkerW oluşturulur → `SetParent` ile pencere WorkerW'ye bağlanır. Explorer çökerse 5sn watchdog otomatik yeniden gömer.
- **Öncelik hesaplama:** Veritabanında saklanmaz, `task_service` her sorguda anlık hesaplar.
