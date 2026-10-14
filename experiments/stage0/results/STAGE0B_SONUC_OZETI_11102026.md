# Aşama 0b sonuç özeti

Koşu 11 Ekim 2026, 02:39 UTC. Betik `stage0b_kosum_v1.py`, ön kayıt `00_ONKAYIT_STAGE0_IKINCI_VERI_v1.md` (10 Eylül 2026, Şerh 1 ve Şerh 2 ile). Kriptografik hat cdsa-bb3 deposunun modülleridir. Sonuç dosyası `sonuclar/stage0b_sonuclar_v1.json`, SHA-256 `b9750beaa64aa8b2e6c26345efd8cd7bb4f135bae7f28ae532f60bba68d28e97`.

## Veri kaynağı

Dört kaynak dosya PhysioNet resmi SHA-256 özetleriyle bayt düzeyinde aynıdır (`veri_b/RESMI_OZETLER.txt`). `.dat` dosyalarını Mete Cantekin tarayıcıyla indirmiştir. Başlık dosyaları tarayıcıda metin olarak açıldığı için metinden yeniden yazılmış ve resmi özetle eşleştirilmiştir. Sonuç dosyasındaki `downloaded_at_utc` alanı dosyanın koşuda okunup özetlendiği anı gösterir, indirme anını değil. Gürültü kaydı `nstdb_bw` kaynak çalışmanın dosyasıdır.

## Karar kuralları

S0B.1 hat genelliği GEÇTİ. Altı kabul ölçütü iki kolda da sağlandı.
S0B.2 öngörü TUTTU. Kol B'de eşlenik iki çiftte kesinti penceresi daha uzun ve oran 1,5'in üzerinde.

## Pencere değerleri (S0B.3 gereği hepsi)

| Kol | Çift | Teslim | En uzun pencere (kayıp / kesinti, s) | Oran | Öngörüye konu |
|---|---|---|---|---|---|
| B, mitdb 234, 600 s | %1 / 5 s | 594 / 595 | 225 / 298 | 1,32 | hayır (Şerh 1) |
| B | %5 / 30 s | 570 / 570 | 77 / 285 | 3,70 | evet, tuttu |
| B | %10 / 60 s | 540 / 540 | 45 / 270 | 6,00 | evet, tuttu |
| C, bidmc01 PPG, 480 s | %1 / 5 s | 475 / 475 | 321 / 238 | 0,74 | hayır (Şerh 2) |
| C | %5 / 30 s | 456 / 450 | 60 / 225 | 3,75 | hayır (Şerh 2) |
| C | %10 / 60 s | 432 / 420 | 30 / 210 | 7,00 | hayır (Şerh 2) |

Kol C'de 480 pakette teslimi eşleşen tek çift %1 / 5 s çiftidir ve orada yön tersine dönmüştür (321 saniyeye karşı 238). Bu, Şerh 1'deki tohum taramasının bu çift için gösterdiği kararsızlıkla tutarlıdır. Düşük kayıp düzeyinde desenin miktara baskın çıktığı söylenemez.

## Yorum sınırı

Denek sayısı üçe, modalite sayısı ikiye çıkmıştır. Sonuç taşıma ve erişim denetimi hattına aittir. Sensör doğruluğu, pilot durumu sınıflandırması, fizyolojik nedensellik ve mevzuat uyumu hakkında hiçbir sonuç kurulmaz.
