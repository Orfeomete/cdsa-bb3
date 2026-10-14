#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C makalesi — kanit AKISI butunlugu testi, 11.09.2026.

NEDEN. C'nin savi kanit butunlugudur. On kayitli calisma on dort kosul
sinadi ve kurcalama kosulu TEK BAYT degistirmeyi sinadi. Ne var ki bir kanit
akisi icin adli bilisim okurunun soracagi sorular baskadir:

  paket SILINIRSE       yakalanir mi
  paketin YERI DEGISIRSE yakalanir mi
  paket YENIDEN OYNATILIRSA yakalanir mi
  akis KESILIRSE        yakalanir mi
  baska bir senaryonun zarfi YERINE KONURSA yakalanir mi

Bu sorular yeni veri gerektirmez. Ayni kayit 100, ayni gercek kriptografik
uygulama, sadece farkli saldirilar.

KOD OKUNDUKTAN SONRAKI GOZLEM, testten once yazilir. kayit_desifre() AAD'yi
ZARFIN KENDISINDEN aliyor ve beklenen bir degerle karsilastirmiyor. Buradan
sunu bekliyorum: yayimlanmis hat ZARF dogrulamasi yapiyor, AKIS dogrulamasi
yapmiyor. Yani tek bayt kurcalama yakalanacak, silme ve yer degistirme
yakalanmayacak.

BEKLENTI TESTTEN ONCE SABITLENIR (post hoc olmasin diye):
  V1 (yayimlanmis hat)  yalniz tek bayt kurcalamayi yakalar
  V2 (akis dogrulayici) sekiz saldirinin hepsini yakalar
Beklenti tutmazsa AYNEN raporlanir; V1 beklenenden fazlasini yakalarsa
gozlemim yanlis demektir ve oyle yazilir.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

UP = Path('/mnt/user-data/uploads/KARAKUTU3.0/CDSA-BB3')
sys.path.insert(0, str(UP / '12_GitHub_Repo/cdsa-bb3'))
from src.cryptography.aes_gcm import kayit_desifre, kayit_sifrele  # noqa
from cryptography.exceptions import InvalidTag                      # noqa

FS, SECONDS = 360, 600
TOPLAM = SECONDS
KAYIT = 'mitdb-1.0.0-record-100'
SENARYO = 'STAGE0B-akis-butunlugu'

BEKLENTI = {
    'tamper_one_byte': {'V1': True, 'V2': True},
    'delete_one': {'V1': False, 'V2': True},
    'delete_block_10': {'V1': False, 'V2': True},
    'swap_two': {'V1': False, 'V2': True},
    'reverse_window_20': {'V1': False, 'V2': True},
    'replay_one': {'V1': False, 'V2': True},
    'truncate_tail_30': {'V1': False, 'V2': True},
    'foreign_envelope': {'V1': False, 'V2': True},
}


def coz_212(yol: Path, ornek: int) -> np.ndarray:
    raw = np.fromfile(yol, dtype=np.uint8)
    u = raw[: (len(raw) // 3) * 3].reshape(-1, 3)
    a = u[:, 0].astype(np.int16) | ((u[:, 1] & 0x0F).astype(np.int16) << 8)
    b = u[:, 2].astype(np.int16) | ((u[:, 1] & 0xF0).astype(np.int16) << 4)
    a = np.where(a >= 2048, a - 4096, a).astype(np.int16)
    b = np.where(b >= 2048, b - 4096, b).astype(np.int16)
    return np.column_stack((a, b))[:ornek]


def paketle(arr, senaryo):
    return [{'dataset': KAYIT, 'scenario': senaryo, 'packet_id': i,
             'sample_start': i * FS, 'sample_count': FS,
             'samples': arr[i * FS:(i + 1) * FS].tolist()}
            for i in range(TOPLAM)]


def muhurle(paketler, anahtar, senaryo):
    return [kayit_sifrele(p, anahtar, senaryo, 'packet-%04d' % p['packet_id'])
            for p in paketler]


# =====================================================================
# IKI DOGRULAYICI
# =====================================================================
def V1_zarf(zarflar, anahtar, beklenen):
    """Yayimlanmis hattin yaptigi sey. Her zarf KENDI AAD'siyle cozulur,
    GCM etiketi gecerliyse kabul edilir. Akis hakkinda hicbir sey
    dogrulanmaz."""
    kabul, red = 0, 0
    for z in zarflar:
        try:
            kayit_desifre(z, anahtar)
            kabul += 1
        except (InvalidTag, ValueError, KeyError):
            red += 1
    return {'kabul': kabul, 'red': red,
            'saptadi': red > 0}


def V2_akis(zarflar, anahtar, beklenen):
    """Akis dogrulayici. V1'in yaptigina ek olarak dort sey denetlenir:
      1  AAD beklenen baglamla birebir mi
      2  paket kimlikleri 0..N-1 tam dizisini olusturuyor mu
      3  hicbir kimlik YINELENMIYOR mu
      4  toplam sayi beklenen sayiya esit mi
    """
    kabul, red = 0, 0
    gorulen = []
    bulgu = []
    for z in zarflar:
        try:
            p = kayit_desifre(z, anahtar)
        except (InvalidTag, ValueError, KeyError):
            red += 1
            bulgu.append('kimlik doğrulama hatası')
            continue
        beklenen_aad = '%s|packet-%04d|KARAKUTU-v1' % (beklenen['senaryo'],
                                                       p['packet_id'])
        if z['aad'] != beklenen_aad:
            red += 1
            bulgu.append('AAD beklenen bağlamla uyuşmuyor')
            continue
        if p['dataset'] != beklenen['kayit']:
            red += 1
            bulgu.append('kayıt kimliği beklenenden farklı')
            continue
        gorulen.append(p['packet_id'])
        kabul += 1
    eksik = sorted(set(range(beklenen['toplam'])) - set(gorulen))
    yinelenen = sorted({i for i in gorulen if gorulen.count(i) > 1})
    sirasiz = gorulen != sorted(gorulen)
    sayi_yanlis = len(gorulen) != beklenen['toplam']
    if eksik:
        bulgu.append('eksik paket kimliği: %d adet' % len(eksik))
    if yinelenen:
        bulgu.append('yinelenen paket kimliği: %s' % yinelenen[:3])
    if sirasiz:
        bulgu.append('paket sırası bozulmuş')
    if sayi_yanlis:
        bulgu.append('paket sayısı beklenenden farklı (%d/%d)'
                     % (len(gorulen), beklenen['toplam']))
    return {'kabul': kabul, 'red': red, 'eksik': len(eksik),
            'yinelenen': len(yinelenen), 'sirasiz': sirasiz,
            'sayi_yanlis': sayi_yanlis,
            'saptadi': bool(red or eksik or yinelenen or sirasiz
                            or sayi_yanlis),
            'bulgu': sorted(set(bulgu))}


# =====================================================================
# SALDIRILAR
# =====================================================================
def saldiri(ad, zarflar, yabanci):
    z = [dict(x) for x in zarflar]
    if ad == 'tamper_one_byte':
        c = bytearray.fromhex(z[300]['sifreli'])
        c[len(c) // 2] ^= 1
        z[300]['sifreli'] = c.hex()
    elif ad == 'delete_one':
        del z[300]
    elif ad == 'delete_block_10':
        del z[200:210]
    elif ad == 'swap_two':
        z[100], z[400] = z[400], z[100]
    elif ad == 'reverse_window_20':
        z[150:170] = list(reversed(z[150:170]))
    elif ad == 'replay_one':
        z[300] = dict(z[299])
    elif ad == 'truncate_tail_30':
        z = z[:-30]
    elif ad == 'foreign_envelope':
        z[300] = dict(yabanci)
    else:
        raise ValueError(ad)
    return z


def main():
    import os
    sinyal = coz_212(UP / '13_STAGE0_GERCEK_VERI/veri/mitdb_100.dat',
                     FS * SECONDS)
    assert len(sinyal) == FS * SECONDS, len(sinyal)
    ozet = hashlib.sha256(
        (UP / '13_STAGE0_GERCEK_VERI/veri/mitdb_100.dat').read_bytes()
    ).hexdigest()
    print('kaynak: mitdb_100.dat sha256 %s...' % ozet[:16])
    anahtar = os.urandom(32)
    paketler = paketle(sinyal, SENARYO)
    zarflar = muhurle(paketler, anahtar, SENARYO)
    # baska bir senaryodan gecerli bir zarf
    yabanci = muhurle(paketle(sinyal, 'STAGE0B-baska-senaryo')[:1],
                      anahtar, 'STAGE0B-baska-senaryo')[0]
    beklenen = {'senaryo': SENARYO, 'kayit': KAYIT, 'toplam': TOPLAM}

    print('\ntemiz akış denetimi')
    for ad, f in (('V1', V1_zarf), ('V2', V2_akis)):
        r = f(zarflar, anahtar, beklenen)
        print('  %s saptadı: %-5s (kabul %d)' % (ad, r['saptadi'], r['kabul']))
        assert not r['saptadi'], '%s temiz akışta yanlış alarm verdi' % ad

    print('\n%-20s %-24s %-24s %s'
          % ('saldırı', 'V1 yayımlanmış hat', 'V2 akış doğrulayıcı',
             'beklenti tuttu mu'))
    sonuc = []
    for ad in BEKLENTI:
        z = saldiri(ad, zarflar, yabanci)
        r1 = V1_zarf(z, anahtar, beklenen)
        r2 = V2_akis(z, anahtar, beklenen)
        b = BEKLENTI[ad]
        tuttu = (r1['saptadi'] == b['V1']) and (r2['saptadi'] == b['V2'])
        print('%-20s %-24s %-24s %s'
              % (ad,
                 'SAPTADI' if r1['saptadi'] else 'saptamadı',
                 'SAPTADI' if r2['saptadi'] else 'saptamadı',
                 'evet' if tuttu else 'HAYIR'))
        sonuc.append({'saldiri': ad, 'V1_saptadi': r1['saptadi'],
                      'V2_saptadi': r2['saptadi'],
                      'V2_bulgu': r2['bulgu'],
                      'beklenti': b, 'beklenti_tuttu': tuttu})

    v1 = sum(1 for x in sonuc if x['V1_saptadi'])
    v2 = sum(1 for x in sonuc if x['V2_saptadi'])
    hepsi = all(x['beklenti_tuttu'] for x in sonuc)
    print('\n' + '=' * 72)
    print('V1 yayımlanmış hat  : %d/%d saldırıyı saptıyor' % (v1, len(sonuc)))
    print('V2 akış doğrulayıcı : %d/%d saldırıyı saptıyor' % (v2, len(sonuc)))
    print('önceden yazılan beklentinin tamamı tuttu mu: %s' % hepsi)
    if not hepsi:
        print('BEKLENTİ TUTMADI — kod okumasına dayanan gözlemim yanlış '
              'çıktı, makaleye bu haliyle yazılacak.')
    Path('/home/claude/kkt/c_akis_butunlugu_sonuc.json').write_text(
        json.dumps({'kaynak_sha256': ozet, 'paket': TOPLAM,
                    'senaryo': SENARYO, 'beklenti': BEKLENTI,
                    'sonuc': sonuc, 'V1_saptadi': v1, 'V2_saptadi': v2,
                    'beklentinin_tamami_tuttu': hepsi},
                   indent=1, ensure_ascii=False), encoding='utf-8')
    print('-> c_akis_butunlugu_sonuc.json')


if __name__ == '__main__':
    main()
