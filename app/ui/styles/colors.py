# Koyu tema renk paleti (Catppuccin Mocha bazlı)

BG_PRIMARY   = "#1E1E2E"   # Ana arka plan
BG_SECONDARY = "#313244"   # Kart / panel arka planı
BG_TERTIARY  = "#45475A"   # Hover, border
BG_INPUT     = "#181825"   # Input alanları

TEXT_PRIMARY   = "#CDD6F4"  # Ana metin
TEXT_SECONDARY = "#BAC2DE"  # İkincil metin
TEXT_MUTED     = "#6C7086"  # Soluk metin, placeholder

ACCENT       = "#89B4FA"   # Mavi vurgu (butonlar, seçili)
ACCENT_HOVER = "#B4BEFE"   # Hover durumu

SUCCESS = "#A6E3A1"   # Yeşil (tamamlandı)
WARNING = "#F9E2AF"   # Sarı (yaklaşan)
ERROR   = "#F38BA8"   # Kırmızı (gecikmiş)
ORANGE  = "#FAB387"   # Turuncu (kritik)

BORDER        = "#45475A"
BORDER_FOCUS  = "#89B4FA"

SCROLLBAR_BG     = "#1E1E2E"
SCROLLBAR_HANDLE = "#45475A"

# Öncelik renk haritası (priority.py sabitleriyle eşleşir)
PRIORITY_COLORS = {
    5: ERROR,    # Gecikmiş
    4: ORANGE,   # < 2 saat
    3: WARNING,  # 2-24 saat
    2: ACCENT,   # Bugün, saatsiz
    1: TEXT_PRIMARY,  # Normal
    0: TEXT_MUTED,    # Tamamlandı
}
