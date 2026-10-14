# BB3 Stage 0 gerçek sinyal veri hattı ön kaydı

Tarih 23 Ağustos 2026

Durum sonuç görülmeden donduruldu

Görev KKT-20260823-014

## Amaç

Bu çalışma AES-256-GCM ve Shamir iki bölü üç erişim hattının gerçek ECG bayt akışıyla bozulma, kayıp, kopma ve gecikme koşullarındaki teknik davranışını sınar. Pilot stresi, hipoksi, iş yükü, klinik tanı, uçuş emniyeti etkisi veya mevzuat uyumu sınanmaz. Stage 0 fizyolojik model doğrulaması değil veri hattı fizibilite sınamasıdır.

## Açık veri kaynakları

Birincil sinyal PhysioNet MIT-BIH Arrhythmia Database sürüm 1.0.0 içindeki kayıt 100 olacaktır. Gürültü kaynağı PhysioNet MIT-BIH Noise Stress Test Database sürüm 1.0.0 içindeki temel gezinme gürültüsü kaydı `bw` olacaktır. Her iki kaynak hesapsız ve açık erişimlidir.

Kaynak dosyaların indirme adresi, indirme zamanı, bayt boyutu ve SHA-256 özeti sonuç kaydına yazılacaktır. Kaynak dosyalar değiştirilmeden saklanacaktır.

## Örneklem ve paketleme

Kayıt 100 ve `bw` dosyalarının ilk on dakikası kullanılacaktır. MIT-BIH 212 biçimi iki kanallı örneklere çözülecektir. Analiz birimi on saniyelik pencere ve ağ birimi bir saniyelik paket olacaktır. Her pakette sıralı paket kimliği, örnek başlangıcı, örnek sayısı, iki kanallı sayısal örnekler ve senaryo kimliği bulunacaktır.

## Dondurulmuş tohum ve tekrar

Rastgele tohum `20260823` olacaktır. Her senaryo aynı paket dizisi üzerinde koşacaktır. İşlevsel oranlar tek deterministik geçişten, zaman ölçümleri aynı paketin on tekrarından raporlanacaktır. Sonuç görüldükten sonra tohum, pencere, paket veya tekrar sayısı değiştirilmeyecektir.

## Bozulma senaryoları

1. Temiz gerçek ECG
2. Gürültü bindirme SNR 24 dB
3. Gürültü bindirme SNR 12 dB
4. Gürültü bindirme SNR 6 dB
5. Paket kaybı yüzde 1
6. Paket kaybı yüzde 5
7. Paket kaybı yüzde 10
8. Kopma 5 saniye
9. Kopma 30 saniye
10. Kopma 60 saniye
11. İletim gecikmesi 50 milisaniye
12. İletim gecikmesi 250 milisaniye
13. İletim gecikmesi 1000 milisaniye
14. Şifreli pakette tek bayt kurcalama

Gecikme fiziksel bekleme ile uygulanmayacaktır. Paket zaman damgasına dondurulmuş gecikme eklenerek kurtarılabilir kanıt penceresi ve uçtan uca zaman bütçesi hesaplanacaktır. Böylece duvar saati yapay biçimde uzatılmadan aynı senaryo birebir üretilebilir.

## Kriptografik hat

Her koşum için 32 baytlık AES anahtarı dondurulmuş tohumdan türetilmeyecek, işletim sistemi güvenli rastgele kaynağından üretilecektir. Tekrarlanabilirlik için anahtarın kendisi değil anahtar SHA-256 özeti kaydedilecektir. AES-256-GCM nonce değeri paket başına benzersiz 12 bayt olacaktır. AAD alanı veri kümesi sürümü, kayıt kimliği, senaryo, paket kimliği ve şema sürümünü bağlayacaktır.

Anahtar mevcut BB3 Shamir uygulamasıyla üç paya ayrılacak ve üç olası ikili pay birleşiminin tamamı sınanacaktır. Tek payla yeniden kurma uygulama düzeyinde reddedilecektir. Düz metin ve anahtar sonuç dosyasına yazılmayacaktır.

## Metrikler

- Bütünlük doğrulama oranı
- Kurcalanmış paket ret oranı
- Üç ikili pay birleşiminde anahtar yeniden kurma oranı
- Tek pay erişim ret oranı
- Paket başına şifreleme ve çözme gecikmesinin ortanca ve yüzde 95 değeri
- Düz metin ile şifreli kayıt arasındaki depolama yükü
- Teslim edilen doğrulanmış paketlerin toplam zaman çizelgesine oranı olarak kurtarılabilir kanıt penceresi
- İlk ve son doğrulanmış paket arasındaki en uzun kesintisiz kanıt aralığı

## Ön kayıtlı kabul ölçütleri

Temiz ve gürültülü teslim edilen paketlerde AES-GCM bütünlük doğrulama oranı yüzde 100 olmalıdır. Kurcalanmış paketlerin yüzde 100'ü doğrulama hatasıyla reddedilmelidir. Üç ikili Shamir birleşiminin yüzde 100'ü aynı AES anahtarını kurmalıdır. Tek pay erişim girişimlerinin yüzde 100'ü uygulama katmanında reddedilmelidir.

Paket başına kriptografik ek depolama yükü nonce ve GCM etiketi ile zorunlu şema alanları dışında büyümemelidir ve gerçek gözlenen bayt değeri raporlanmalıdır. Gecikmenin yüzde 95 değeri kullanılan makineyle birlikte raporlanacaktır. Yüzde 95 kriptografik işlem gecikmesi 100 milisaniyeyi aşarsa gerçek zamanlı paketleme kabul ölçütü sağlanmamış sayılacaktır.

Kayıp ve kopma senaryolarında doğrulanmış paketler yanlış veya doldurulmuş veriyle değiştirilmemelidir. Kurtarılabilir kanıt penceresi dondurulmuş kayıp düzeninin teslim ettiği özgün paket oranıyla birebir eşleşmelidir. Bir paket bile sessizce bozulmuş olarak kabul edilirse çalışma başarısız sayılacaktır.

## Tekrarlanabilirlik

Koşum betiği sürümlü olarak bu klasörde tutulacaktır. Python sürümü, bağımlılık sürümleri, işletim sistemi, işlemci, kaynak dosya özetleri, komut, tohum ve senaryo yapılandırması JSON sonuç dosyasına yazılacaktır. Sonuçlar bu ön kayıt metnine dokunmadan ayrı dosyalara yazılacaktır.

## Yorum sınırı

Başarılı sonuç yalnız gerçek ECG bayt akışının tanımlı kriptografik hattan geçirilebildiğini ve ön kayıtlı bozulmalar altında kayıt bütünlüğünün nasıl korunduğunu gösterir. Sensör doğruluğu, pilot durumu sınıflandırması, nedensel fizyolojik açıklama, operasyonel emniyet yararı, Just Culture garantisi veya mevzuat uyumu hakkında sonuç kurulamaz.

