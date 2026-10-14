"""Tek pay denetimi, 14.10.2026 (ön kayıtlı değil, sonradan yapılmış denetim).

Aşama 0 ve Aşama 0b koşum betikleri tek pay ölçütünü sabit True olarak yazmıştı
(stage0_kosum_v1.py ve stage0b_kosum_v1.py, single_share_rejected = [True, True, True]).
Bu betik ölçütü gerçekten sınar. cdsa-bb3 deposunun shamir ve aes_gcm modülleriyle
bir anahtar üç paya bölünür, her pay tek başına birleştirme işlevine verilir,
dönen değerin anahtardan farklı olduğu ve bu değerle deşifrelemenin kimlik
doğrulamasında düştüğü denetlenir. Üç ikili birleşim de yeniden sınanır.
Tekrar sayısı 1000 anahtardır.
"""
import json, os, sys, hashlib, platform
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '12_GitHub_Repo' / 'cdsa-bb3'))
from src.cryptography.shamir import anahtari_paylaristir, anahtari_birlestir, P
from src.cryptography.aes_gcm import kayit_sifrele, kayit_desifre
from cryptography.exceptions import InvalidTag
import cryptography, itertools

TEKRAR = 1000
tek_farkli = tek_dogrulama_dustu = ikili_dogru = 0
tek_toplam = ikili_toplam = 0
tek_hata_turu = {}
for t in range(TEKRAR):
    anahtar = os.urandom(32)
    paylar = anahtari_paylaristir(int.from_bytes(anahtar, 'big'), n=3, k=2)
    zarf = kayit_sifrele({'packet_id': t, 'samples': [1, 2, 3]}, anahtar, 'TEK-PAY', 'packet-%04d' % t)
    for pay in paylar:
        tek_toplam += 1
        deger = anahtari_birlestir([pay])
        if deger != int.from_bytes(anahtar, 'big'):
            tek_farkli += 1
        try:
            aday = (deger % (1 << 256)).to_bytes(32, 'big') if deger >= (1 << 256) else deger.to_bytes(32, 'big')
            kayit_desifre(zarf, aday)
        except InvalidTag:
            tek_dogrulama_dustu += 1
        except Exception as e:
            tek_hata_turu[type(e).__name__] = tek_hata_turu.get(type(e).__name__, 0) + 1
            tek_dogrulama_dustu += 1
    for ikili in itertools.combinations(paylar, 2):
        ikili_toplam += 1
        ikili_dogru += int(anahtari_birlestir(list(ikili)).to_bytes(32, 'big') == anahtar)

sonuc = {
    'tarih_utc': datetime.now(timezone.utc).isoformat(),
    'onkayitli': False,
    'not': 'Shamir modulu pay sayisini denetlemez, tek pay verildiginde f(x_i) dondurur. Red uygulama katmaninda degil, yanlis anahtarin GCM dogrulamasinda gerceklesir.',
    'tekrar_anahtar': TEKRAR,
    'tek_pay_deneme': tek_toplam,
    'tek_pay_anahtardan_farkli': tek_farkli,
    'tek_pay_desifre_reddedildi': tek_dogrulama_dustu,
    'tek_pay_diger_hata': tek_hata_turu,
    'ikili_deneme': ikili_toplam,
    'ikili_dogru_anahtar': ikili_dogru,
    'python': sys.version.split()[0],
    'platform': platform.platform(),
    'cryptography': cryptography.__version__,
    'betik_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
(HERE / 'sonuclar' / 'tek_pay_denetimi_14102026.json').write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps(sonuc, ensure_ascii=False, indent=1))
