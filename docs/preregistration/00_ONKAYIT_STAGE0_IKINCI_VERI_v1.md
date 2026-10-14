# C makalesi — Aşama 0'ın ikinci ve üçüncü gerçek veri kümesine genişletilmesi ön kaydı

Tarih 10 Eylül 2026

Durum **veri indirilmeden ve görülmeden donduruldu**

Görev KKT-20260910-STAGE0B

Kaynak ön kayıt `00_STAGE0_ON_KAYIT_v1.md` (23 Ağustos 2026). Bu metin onun
uzantısıdır ve onu değiştirmez.

---

## Neyi kapatmak için

C makalesinin en pahalı sınırlılığı tektir. Kanıt **tek kayıt, tek denek,
istirahatte ve klinik bir veri tabanından** gelmektedir. Ön kayıtlı çalışma
MIT-BIH Aritmi Veri Tabanı kayıt 100'ün ilk 600 saniyesi üzerinde koşmuştur.

Bu uzantı iki ayrı genellik sorusunu ayrı ayrı sınar.

**Denek genelliği.** Aynı veri tabanından farklı bir denek. Taşıma yolunun
davranışı deneğe bağlı mı.

**Sinyal genelliği.** Farklı bir veri tabanı, farklı bir modalite ve farklı bir
örnekleme hızı. Hat baytlar üzerinde çalıştığı için modaliteden bağımsız
olması beklenir, ne var ki bu beklenti şimdiye kadar **sınanmadı**, yalnız
varsayıldı. Makalenin sinyalleri HRV, SpO2 ve GSR olduğu için EKG dışında bir
modalitenin sınanması savın kapsamı bakımından önemlidir.

## Veri kaynakları

**Kol B, denek genelliği.** PhysioNet MIT-BIH Arrhythmia Database sürüm 1.0.0
içindeki **kayıt 234**. İki kanal, 360 Hz, 212 biçimi. Kayıt 100 ile aynı veri
tabanı, farklı denek.

**Kol C, sinyal genelliği.** PhysioNet **BIDMC PPG and Respiration Dataset**
sürüm 1.0.0 içindeki **kayıt bidmc01**. Fotopletismografi kanalı, 125 Hz.
Farklı veri tabanı, farklı modalite, farklı örnekleme hızı, farklı denek.

Gürültü kaynağı her iki kolda da değişmez, MIT-BIH Noise Stress Test Database
sürüm 1.0.0 içindeki temel gezinme kaydı `bw`.

Her kaynak dosyanın indirme adresi, indirme zamanı, bayt boyutu ve SHA-256
özeti sonuç kaydına yazılacaktır. Kaynak dosyalar değiştirilmeden
saklanacaktır.

## Örneklem ve paketleme

Her iki kolda da ilk **600 saniye** kullanılacaktır, böylece paket sayısı
kayıt 100 ile aynı, yani 600 kalır ve pencere sayıları doğrudan
karşılaştırılabilir olur. Analiz birimi on saniyelik pencere, ağ birimi bir
saniyelik paket. Kol C'de paket başına örnek sayısı 125 olacaktır, çünkü
örnekleme hızı farklıdır; paket **süresi** sabit tutulur, örnek sayısı değil.

## Dondurulmuş tohum, ve neden yeni bir tohum

Tohum **20260910** olacaktır. **Kaynak çalışmanın tohumu 20260823 bilerek
yeniden kullanılmayacaktır** ve nedeni şudur.

Kayıp deseni, tohum ile paket sayısı verildiğinde tamamen belirlenimlidir.
Aynı tohum ve aynı 600 paket kullanılırsa kayıp deseni birebir aynı çıkar,
dolayısıyla en uzun kesintisiz pencere değerleri de kayıttan bağımsız olarak
birebir aynı çıkar. Böyle bir koşum hiçbir şeyi çoğaltmaz, yalnız aritmetiği
tekrar eder.

Yeni tohumla kayıp deseni değişir ve asıl soru sorulabilir hâle gelir.
**Manşet bulgu farklı bir desen altında da tutuyor mu.**

## Bozulma senaryoları

Kaynak ön kaydın on dört senaryosu **değiştirilmeden** uygulanacaktır. Temiz
taban; 24, 12 ve 6 dB gürültü; yüzde 1, 5 ve 10 paket kaybı; 5, 30 ve 60
saniye kopma; 50, 250 ve 1000 milisaniye gecikme; şifreli pakette tek bayt
kurcalama.

## Kriptografik hat

Değiştirilmez. AES-256-GCM, paket başına benzersiz 96 bit nonce, AAD alanına
veri kümesi sürümü, kayıt kimliği, senaryo, paket kimliği ve şema sürümünün
bağlanması, Shamir iki bölü üç, üç ikili birleşimin tamamının sınanması, tek
payın uygulama katmanında reddi. Anahtar işletim sisteminin güvenli rastgele
kaynağından üretilir, yalnız SHA-256 özeti kaydedilir.

## Ön kayıtlı kabul ölçütleri

Kaynak ön kaydın altı ölçütü **değiştirilmeden** geçerlidir. Teslim edilen
paketlerde bütünlük yüzde 100, kurcalanan paketlerin yüzde 100 reddi, üç ikili
Shamir birleşiminin yüzde 100 anahtar kurması, tek pay girişimlerinin yüzde
100 reddi, ek yükün nonce ve etiket dışında büyümemesi, 95. yüzdebirlik
kriptografik gecikmenin 100 milisaniyeyi aşmaması.

## Önceden yazılmış öngörü ve karar kuralı

**Kural S0B.1, hat genelliği.** Altı kabul ölçütü her iki kolda da
sağlanmalıdır. Bir kolda sağlanmazsa şu cümle yazılır:

> Taşıma ve erişim denetimi hattı, sınanan ikinci veri kümesinde ön kayıtlı
> kabul ölçütlerini karşılamamıştır ve hattın modaliteden bağımsız olduğu savı
> geri çekilmektedir.

**Kural S0B.2, manşet bulgunun çoğaltılması.** Kaynak çalışmada eşit teslimde
kaybın deseni miktarına baskın çıkmıştır. Yüzde 10 dağınık kayıp ile 60
saniyelik tek kopma aynı 540 paketi teslim etmiş, en uzun kesintisiz pencere
40 saniyeye karşı 270 saniye, yani 6,75 kat olmuştur.

**Öngörü, veriye bakılmadan yazılıyor.** Her iki kolda da eşleşen çiftlerde
kopma kolunun en uzun penceresi kayıp kolunun penceresinden **büyük**
olacaktır ve oran **1,5 katın üzerinde** kalacaktır.

Öngörü tutmazsa şu cümle yazılır:

> Kaybın deseninin miktarına baskın çıkması, kaynak çalışmanın dondurulmuş
> kayıp desenine özgü bir gözlemdir ve farklı bir desen altında
> çoğaltılamamıştır; bulgu bu haliyle genel bir taşıma bütçesi savı olarak
> sunulamaz.

**Kural S0B.3.** Üç kolun tamamının pencere değerleri ve oranları, hangi cümle
yazılırsa yazılsın tabloya girecektir. Öngörüye uymayan bir kol tablodan
çıkarılmayacaktır.

## Sonuç görüldükten sonra değiştirilmeyecekler

Kayıt seçimleri, süre, tohum, senaryo listesi, kabul ölçütleri, S0B.2'nin 1,5
kat eşiği, paket süresinin bir saniye olması.

## Yorum sınırı

Başarılı sonuç, hattın üç gerçek kayıtta ve iki modalitede ön kayıtlı
bozulmalar altında kanıt bütünlüğünü koruduğunu gösterir. Denek sayısı üçe
çıkmış olur, bu da bir uçuş güvertesi savı için hâlâ yetersizdir. Sensör
doğruluğu, pilot durumu sınıflandırması, fizyolojik nedensellik ve mevzuat
uyumu hakkında hiçbir sonuç kurulamaz.

---

*Bu metin veri indirilmeden yazılmış ve dondurulmuştur. Sonuçlar bu dosyaya
dokunulmadan ayrı dosyalara yazılacaktır.*

---

# ŞERH 1 — 10 Eylül 2026, veri hâlâ indirilmemişken

Bu şerh, ön kayıt dondurulduktan sonra ve **hiçbir gerçek kayıt indirilmeden**
yazılmıştır. Eklenmesinin nedeni, S0B.2'nin eşiğini yazarken yaptığım bir
belirtim hatasıdır.

## Neyi fark ettim

En uzun kesintisiz kanıt penceresi, hangi paketlerin teslim edildiğine bağlıdır
ve bunu belirleyen şey **tohum ile paket sayısıdır**. Sinyalin içeriğiyle
ilgisi yoktur. Dolayısıyla bu değerler gerçek kayıt indirilmeden hesaplanabilir
ve veri geldiğinde değişmez.

Boru hattı sınamasında görüldü ki uzantı tohumu 20260910 altında yüzde 1 ile
5 saniye çiftinin oranı **1,32** çıkıyor, yani yazdığım 1,5 eşiğinin altında.
Bu, veriye bakılmadan görülen bir aritmetik olgudur.

## Ne yaptım

Eşiği gevşetmek yerine olguyu ölçtüm. `desen_tohum_taramasi.py` betiği üç
çiftin oranını **2000 tohum** üzerinde hesapladı. Sonuç şudur.

| Çift | Ortanca | En küçük | En büyük | 1,5 üstü | Yön korunan tohum | Kaynak tohumun yüzdebirliği |
|---|---:|---:|---:|---:|---:|---:|
| %1 / 5 s | 1,42 | 0,61 | 2,84 | 815/2000 | **1776/2000** | 59. |
| %5 / 30 s | 3,96 | 1,44 | 7,31 | 1999/2000 | 2000/2000 | 47. |
| %10 / 60 s | 6,59 | 2,90 | 11,74 | 2000/2000 | 2000/2000 | 60. |

**Not, bir önceki taslakta yaptığım yuvarlama hatası.** İki güçlü çift için
"1,5 üstü %100" yazmıştım; kesin sayı yüzde 5 çiftinde **1999/2000**'dir, çünkü
en küçük oran 1,44 ile eşiğin hemen altındadır. Yüzde 10 çiftinde oran
gerçekten 2000/2000'dir. Aşağıdaki savlar bu kesin sayılarla kurulmuştur.

İki şey ortaya çıktı.

**Birincisi, manşet bulgu sağlam.** Yüzde 5 ile 30 saniye ve yüzde 10 ile 60
saniye çiftlerinde kopma penceresi **2000 tohumun hepsinde** kayıp
penceresinden büyüktür, yani etkinin yönü hiç tersine dönmez. Oran, yüzde 10
çiftinde 2000 tohumun 2000'inde, yüzde 5 çiftinde 1999'unda 1,5'in
üzerindedir. Kaynak çalışmanın dondurulmuş tohumu elverişli bir çekim de
değildir; bu iki dağılımda 47. ve 60. yüzdebirlikte durur. Yani 6,75 katı
dondurulmuş tek bir desene özgü bir tesadüf değildir. Bu, C makalesi için
gerçek bir güçlenmedir ve yeni veri gerektirmemiştir.

**İkincisi, yüzde 1 ile 5 saniye çifti savı hiç desteklemiyor.** Oran
tohumların yalnız yüzde 40,8'inde 1,5'i geçiyor ve bazı tohumlarda **1'in
altına düşüyor**, yani kayıp penceresi kopma penceresinden büyük çıkıyor.
Yönün kendisi kararsız.

Ayrıca bu çift **teslimde eşleşmiyor**. Yüzde 1 kayıp 594 paket teslim
ederken 5 saniyelik kopma 595 teslim ediyor. Kaynak makale bunu tablosunda
zaten böyle yazıyor ve o çift için "en az ayrışan çift" demekle yetiniyor,
yani eşleşme savı kurmuyor. Ne var ki çiftin aynı tabloda eşleşen çiftlerle
yan yana durması, kurulmayan bir savı kurulmuş gibi okutmaya açıktır.

## S0B.2'nin düzeltilmiş hâli

Öngörü, yalnız yönü kararlı olan iki çift için kurulur.

**S0B.2 (düzeltilmiş).** Yüzde 5 ile 30 saniye ve yüzde 10 ile 60 saniye
çiftlerinde kopma kolunun en uzun penceresi kayıp kolunun penceresinden büyük
olacak ve oran 1,5'in üzerinde kalacaktır.

**S0B.2b.** Yüzde 1 ile 5 saniye çifti tabloya girecek, fakat **öngörüye konu
edilmeyecektir**. Gerekçesi bu şerhte kayıtlıdır: tohum taraması yönünün
kararsız olduğunu göstermiştir ve çift teslimde de eşleşmemektedir.

Bu değişiklik bir gevşetme değildir. Eşiğin sınandığı yeri, kaynak makalenin
fiilen kurduğu savla hizalamaktadır. Gerçek veriye bakılmadan yapılmıştır ve
dayandığı ölçüm veriden bağımsızdır.

## C makalesi için iki öneri, ayrı karar gerektirir

1. **Tohum taraması makaleye girsin.** "Dondurulmuş tek bir desende 6,75 kat
   gözlendi" cümlesi, "2000 desende etki hiç tersine dönmedi ve oran hiç 1,5'in
   altına inmedi" cümlesine dönüşür. Yeni veri gerektirmez.
2. **Üçüncü çiftin sunumu düzeltilsin.** Teslimde eşleşmediği (594'e karşı 595)
   ve yönünün desenler arasında kararlı olmadığı açıkça yazılsın, sınır durumu
   olarak sunulsun.

---

# ŞERH 2 — 10 Eylül 2026, veri hâlâ indirilmemişken

Bu şerh de veri indirilmeden yazılmıştır. Kaynak sayfaları PhysioNet üzerinden
doğrulandıktan sonra iki olgu ortaya çıktı.

## Doğrulananlar

**Kol B sağlam.** MIT-BIH Aritmi Veri Tabanı'nda kayıt 234 vardır, `234.dat`
ve `234.hea` dosyalarıyla. Kayıtlar 360 Hz, her biri otuz dakika. Altı yüz
saniye rahatça sığar.

**Kol C'nin dosya adları doğru.** BIDMC veri tabanında dalga biçimi kayıtları
`bidmc01.dat` ve `bidmc01.hea` adlarını taşır. Sonunda `n` bulunan dosyalar
(`bidmc01n.*`) dalga biçimi değil, 1 Hz sayısal parametrelerdir ve bu çalışmada
kullanılmayacaktır.

## Sorun

**BIDMC kayıtları sekiz dakikadır, yani 480 saniye.** Ön kayıt 600 saniye
istiyordu; 125 Hz'de bu 75 000 örnek eder, oysa kayıtta 60 000 örnek vardır.
Altı yüz saniye sığmamaktadır.

Süre 480'e indirildiğinde ikinci bir sorun doğar. Eşleşen çift tasarımı paket
sayısına bağlıdır, çünkü kopma süreleri sabit saniye cinsindendir ve kısalan
zaman çizelgesinde daha büyük bir oran tutar.

| Çift | 600 paket | 480 paket |
|---|---|---|
| %1 / 5 s | 594'e karşı 595, eşleşmez | 475'e karşı 475, **eşleşir** |
| %5 / 30 s | 570'e karşı 570, **eşleşir** | 456'ya karşı 450, eşleşmez |
| %10 / 60 s | 540'a karşı 540, **eşleşir** | 432'ye karşı 420, eşleşmez |

Yani 480 pakette, S0B.2'nin dayandığı iki güçlü çift teslimde eşleşmiyor.
Eşleşmeyi geri getirmenin tek yolu kopma sürelerini değiştirmek olurdu, o da
"on dört senaryo değiştirilmeden uygulanacaktır" hükmünü bozar.

## Çözüm, iki kolun işi ayrılıyor

**S0B.2b (düzeltilmiş).** Manşet bulgunun çoğaltılması **yalnız Kol B'nin
işidir**. Kol B 600 saniye ve 600 paketle koşar, çiftler kaynak çalışmadaki
gibi birebir eşleşir, öngörü de Şerh 1'deki hâliyle geçerlidir.

**S0B.1b (düzeltilmiş).** Kol C, kaydın tamamı olan **480 saniye** ile koşar
ve işi **hattın modaliteden bağımsızlığını** sınamaktır. Bunu sınayan şey altı
kabul ölçütüdür ve bu ölçütlerin hiçbiri süreye bağlı değildir. Kol C'nin
pencere değerleri ve oranları tabloya girer, fakat **kaynak çalışmayla
doğrudan karşılaştırılamaz** ve S0B.2'nin öngörüsüne konu edilmez. Bu, sonuç
görülmeden şimdi yazılmıştır.

Bu ayrım bir gevşetme değildir. Her kol yanıtlayabildiği soruyu yanıtlar. Kol B
desen sorusunu 600 pakette yanıtlar, Kol C modalite sorusunu 480 pakette
yanıtlar, ve hiçbiri diğerinin yerine geçmez.

## Neden başka bir PPG kaydı seçilmedi

Sekiz dakikadan uzun açık bir PPG kaydı bulmak mümkündür, ne var ki bu
seçimin veriye bakılarak yapılması gerekir ve bu ön kaydın dondurulmuş olma
niteliğini zedeler. BIDMC seçimi bu metnin ilk sürümünde yapılmıştı; süresi
kısa çıktığı için kolun kapsamı daraltılmakta, kayıt değiştirilmemektedir.

---

*Şerh 2 sonu. Kaynaklar PhysioNet BIDMC 1.0.0 ve MIT-BIH Arrhythmia 1.0.0
sayfalarından doğrulanmıştır.*
