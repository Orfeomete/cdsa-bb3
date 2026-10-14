#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C makalesinin mansiet bulgusunun kayip desenine dayanikliligi.

NEDEN BU KOSULABILIYOR. En uzun kesintisiz kanit penceresi, hangi paketlerin
teslim edildigine bagli; hangi paketlerin teslim edildigi ise TOHUM ile paket
sayisi tarafindan belirleniyor. Sinyalin icerigiyle hicbir ilgisi yok. Bu
yuzden bu olcum gercek EKG veya PPG kaydi indirilmeden yapilabilir ve
sonucu veri geldiginde degismez.

NE SINANIYOR. C makalesi su savi kuruyor: esit teslimde kaybin DESENI
miktarina baskin cikar. Kanit olarak uc eslesen cift veriliyor ve en carpici
olani yuzde 10 dagink kayip ile 60 saniyelik tek kopma, ikisi de 540 paket
teslim ederken pencereler 40 ve 270 saniye, yani 6,75 kat.

Akla gelen itiraz: 6,75 sayisi dondurulmus tek bir kayip desenine mi ozgu.
Bu betik itirazi 2000 tohum uzerinde yanitliyor.

Kaynak calismanin tohumu 20260823, uzantinin tohumu 20260910; ikisi de
taramada isaretleniyor.
"""
import json
import random
import statistics

TOPLAM = 600          # kaynak calismayla ayni
CIFTLER = [(1, 5), (5, 30), (10, 60)]
N_TOHUM = 2000
KAYNAK_TOHUM = 20260823
UZANTI_TOHUM = 20260910


def en_uzun(idler):
    if not idler:
        return 0
    en = cur = 1
    for a, b in zip(idler, idler[1:]):
        cur = cur + 1 if b == a + 1 else 1
        en = max(en, cur)
    return en


def kayip_penceresi(pct, rng):
    n = round(TOPLAM * pct / 100)
    atilan = set(rng.sample(range(TOPLAM), n))
    return en_uzun([i for i in range(TOPLAM) if i not in atilan]), TOPLAM - n


def kopma_penceresi(saniye):
    bas = (TOPLAM - saniye) // 2
    kalan = list(range(bas)) + list(range(bas + saniye, TOPLAM))
    return en_uzun(kalan), len(kalan)


def tohum_kos(tohum):
    rng = random.Random(tohum)
    out = []
    for pct, sec in CIFTLER:
        kp, kt = kayip_penceresi(pct, rng)
        op, ot = kopma_penceresi(sec)
        out.append({'cift': '%%%d / %ds' % (pct, sec),
                    'teslim': [kt, ot],
                    'esit_teslim': kt == ot,
                    'pencere': [kp, op],
                    'oran': op / kp if kp else float('inf')})
    return out


# ---------------------------------------------------------------- tarama
tarama = {c: [] for c in ('%1 / 5s', '%5 / 30s', '%10 / 60s')}
esit_teslim_hep = True
for t in range(N_TOHUM):
    for r in tohum_kos(t):
        tarama[r['cift']].append(r['oran'])
        esit_teslim_hep &= r['esit_teslim']

print('KAYIP DESENİ TOHUM TARAMASI — %d tohum, %d paket' % (N_TOHUM, TOPLAM))
print('eşit teslim her tohumda sağlandı mı:', esit_teslim_hep)
print()
print('%-11s %7s %7s %7s %7s %8s %8s' % ('çift', 'ortanca', 'min', 'maks',
                                         'p05', '>1,5 %', '>3 %'))
ozet = {}
for c, v in tarama.items():
    v = sorted(v)
    ozet[c] = {
        'ortanca': round(statistics.median(v), 3),
        'min': round(v[0], 3), 'maks': round(v[-1], 3),
        'p05': round(v[int(0.05 * len(v))], 3),
        'oran_1_5_ustu_yuzde': round(100 * sum(1 for x in v if x > 1.5)
                                     / len(v), 1),
        'oran_3_ustu_yuzde': round(100 * sum(1 for x in v if x > 3) / len(v),
                                   1),
        'her_zaman_1_ustu': v[0] > 1.0,
    }
    o = ozet[c]
    print('%-11s %7.2f %7.2f %7.2f %7.2f %7.1f%% %7.1f%%'
          % (c, o['ortanca'], o['min'], o['maks'], o['p05'],
             o['oran_1_5_ustu_yuzde'], o['oran_3_ustu_yuzde']))

print()
for c, o in ozet.items():
    print('%-11s kopma penceresi her tohumda kayıp penceresinden büyük mü: %s'
          % (c, o['her_zaman_1_ustu']))

print()
for ad, t in (('kaynak çalışma', KAYNAK_TOHUM), ('uzantı', UZANTI_TOHUM)):
    print('%-16s tohum %-9d %s' % (ad, t, '  '.join(
        '%s oran %.2f (pencere %d/%d)'
        % (r['cift'], r['oran'], r['pencere'][0], r['pencere'][1])
        for r in tohum_kos(t))))

json.dump({'toplam_paket': TOPLAM, 'n_tohum': N_TOHUM,
           'esit_teslim_her_tohumda': esit_teslim_hep,
           'ozet': ozet,
           'kaynak_tohum': {'tohum': KAYNAK_TOHUM,
                            'ciftler': tohum_kos(KAYNAK_TOHUM)},
           'uzanti_tohum': {'tohum': UZANTI_TOHUM,
                            'ciftler': tohum_kos(UZANTI_TOHUM)}},
          open('/home/claude/kkt/desen_tohum_taramasi.json', 'w',
               encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> desen_tohum_taramasi.json')
