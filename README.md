# R-minder

Windows masaüstüne gömülü, her zaman görünür bir hatırlatıcı uygulaması.

## Özellikler

- **Masaüstü Widget** — Duvar kağıdının önünde, ikonların arkasında her zaman görünür
- **Bugün / Yarın / Bu Hafta** sekmeleri — görevler gruplara ayrılmış
- **Öncelik Sistemi** — saate yaklaştıkça renk değişir, görev üste çıkar
- **Tekrarlayan Görevler** — günlük, haftalık, aylık, yıllık ve özel kurallar
- **Windows Toast Bildirimleri** — görev zamanı yaklaşınca uyarı
- **Ana Pencere** — tam CRUD, system tray üzerinden erişim
- **Koyu Tema** varsayılan

## Gereksinimler

- Windows 10 / 11
- Python 3.11+ (sistem Python — Anaconda değil)

## Kurulum

```bash
git clone https://github.com/bektasSoftwareEng/R-minder.git
cd R-minder
pip install -r requirements.txt
python main.py
```

> **Not:** Anaconda ortamında PyQt6 DLL hatası alınabilir. Sistem Python ile çalıştır:
> `"C:\Users\<kullanici>\AppData\Local\Programs\Python\Python3xx\python.exe" main.py`

## Proje Yapısı

```
R-minder/
├── main.py                          # Giriş noktası
├── app/
│   ├── core/
│   │   ├── database.py              # SQLite bağlantı ve migration
│   │   ├── models.py                # Veri modelleri (Task, RecurrenceRule...)
│   │   └── repository.py           # CRUD operasyonları
│   ├── services/
│   │   ├── task_service.py          # İş mantığı ve öncelik hesaplama
│   │   ├── recurrence_service.py    # Tekrarlama üretici
│   │   ├── notification_service.py  # Windows Toast bildirimleri
│   │   └── reminder_engine.py       # Arka plan zamanlayıcı
│   ├── ui/
│   │   ├── widget/                  # Masaüstü widget bileşenleri
│   │   ├── main_window/             # Ana uygulama penceresi
│   │   ├── system_tray.py           # System tray ikonu
│   │   └── styles/                  # Tema ve renkler
│   └── utils/
│       ├── config.py                # Uygulama ayarları
│       ├── date_utils.py            # Tarih yardımcıları
│       └── priority.py              # Aciliyet hesaplama
├── data/                            # SQLite veritabanı (git'e dahil değil)
├── assets/                          # İkonlar ve görseller
├── ARCHITECTURE.md                  # Sistem mimarisi detayları
├── ROADMAP.md                       # Geliştirme yol haritası
└── TODO.md                          # Aktif görev listesi
```

## Geliştirme Fazları

| Faz | Konu | Durum |
|-----|------|-------|
| 1 | Temel altyapı (DB, modeller, servisler) | Tamamlandı |
| 2 | Ana pencere ve system tray | Devam ediyor |
| 3 | Masaüstü widget | Bekliyor |
| 4 | Bildirim motoru | Bekliyor |
| 5 | Gelişmiş tekrarlama | Bekliyor |
| 6 | Paketleme (.exe) | Bekliyor |

Detaylar için [ROADMAP.md](ROADMAP.md) ve [ARCHITECTURE.md](ARCHITECTURE.md) dosyalarına bakabilirsin.

## Katkı

Proje modüler yapıda geliştirilmektedir. Her katman bağımsızdır:
- **core/** — sadece veri, UI bilmez
- **services/** — iş mantığı, UI bilmez
- **ui/** — sadece servisleri çağırır, doğrudan DB'ye erişmez
