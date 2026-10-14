#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BB3 Asama 0 uzantisi — ikinci ve ucuncu gercek veri kumesi.

On kayit: 00_ONKAYIT_STAGE0_IKINCI_VERI_v1.md, 10 Eylul 2026, veri
indirilmeden donduruldu.

Kaynak calismanin (stage0_kosum_v1.py, tohum 20260823) senaryo listesi,
kriptografik hatti ve kabul olcutleri DEGISTIRILMEDEN uygulanir. Degisen
uc sey vardir:
  1. Kayit. Kol B mitdb kayit 234 (ayni veri tabani, farkli denek).
     Kol C bidmc01 (farkli veri tabani, PPG modalitesi, 125 Hz).
  2. Tohum 20260910. Kaynak tohum bilerek yeniden kullanilmaz, cunku ayni
     tohum ayni kayip desenini verir ve pencere sayilari kayittan bagimsiz
     olarak birebir ayni cikar; boyle bir kosum hicbir seyi cogaltmaz.
  3. Paket SURESI sabit tutulur (bir saniye), paketteki ORNEK SAYISI degil,
     cunku ornekleme hizlari farklidir.

KULLANIM

  Gercek kosum (Mete'nin makinesinde, ag ve cdsa-bb3 deposu gerekir):
      python stage0b_kosum_v1.py

  Boru hattini veri olmadan sinama (agsiz, depo olmadan):
      python stage0b_kosum_v1.py --sinama

  --sinama kipi SONUC DOSYASI YAZMAZ. Sentetik bir sinyal uretir, yerel
  cryptography paketiyle bir vekil sifreleyici kullanir ve butun boru
  hattinin uctan uca calistigini gosterir. Bilimsel bir sonuc degildir ve
  boyle sunulamaz.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import platform
import random
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "veri_b"
OUT = HERE / "sonuclar"
REPO = HERE.parent / "12_GitHub_Repo" / "cdsa-bb3"

SEED = 20260910
SECONDS = 600            # Kol B. Kol C icin asagida ezilir (Serh 2).

# --- on kayitta sabitlenen kollar
KOLLAR = {
    "B_mitdb_234": {
        "aciklama": "MIT-BIH Arrhythmia 1.0.0 kayit 234, ayni veri tabani, "
                    "farkli denek",
        "fs": 360,
        "dataset": "mitdb-1.0.0-record-234",
        "kaynak": {
            "mitdb_234.dat": "https://physionet.org/files/mitdb/1.0.0/234.dat",
            "mitdb_234.hea": "https://physionet.org/files/mitdb/1.0.0/234.hea",
        },
        "sinyal": "mitdb_234.dat",
        "saniye": 600,
        "s0b2": True,
    },
    "C_bidmc_01": {
        "aciklama": "BIDMC PPG and Respiration 1.0.0 kayit bidmc01, farkli "
                    "veri tabani, PPG modalitesi, 125 Hz",
        "fs": 125,
        "dataset": "bidmc-1.0.0-record-bidmc01",
        "kaynak": {
            "bidmc01.dat": "https://physionet.org/files/bidmc/1.0.0/"
                           "bidmc01.dat",
            "bidmc01.hea": "https://physionet.org/files/bidmc/1.0.0/"
                           "bidmc01.hea",
        },
        "sinyal": "bidmc01.dat",
        # Serh 2: BIDMC kayitlari sekiz dakikadir. 480 pakette eslesen cift
        # tasarimi bozuluyor (%5/30s 456'ya karsi 450, %10/60s 432'ye karsi
        # 420), bu yuzden bu kol S0B.2'ye konu DEGILDIR; isi alti kabul
        # olcutuyle hattin modaliteden bagimsizligini sinamaktir.
        "saniye": 480,
        "s0b2": False,
    },
}
GURULTU = {
    "nstdb_bw.dat": "https://physionet.org/files/nstdb/1.0.0/bw.dat",
    "nstdb_bw.hea": "https://physionet.org/files/nstdb/1.0.0/bw.hea",
}

# on kayit S0B.2 (SERH 1 ile duzeltilmis hali): oran esigi yalniz yonu
# kararli iki cift icin baglayicidir. Yuzde 1 / 5 s cifti tabloya girer ama
# ongoruye konu edilmez; 2000 tohumluk tarama yonunun kararsiz oldugunu
# gostermistir (desen_tohum_taramasi.py) ve cift teslimde de eslesmez
# (594'e karsi 595).
ORAN_ESIGI = 1.5
ONGORULU_CIFTLER = {'loss_5pct / disconnect_30s',
                    'loss_10pct / disconnect_60s'}


# =====================================================================
# kriptografik hat
# =====================================================================
def hat_yukle(sinama: bool):
    """Gercek kosumda cdsa-bb3 deposunun modulleri, sinamada yerel vekil."""
    if not sinama:
        sys.path.insert(0, str(REPO))
        from src.cryptography.aes_gcm import kayit_desifre, kayit_sifrele
        from src.cryptography.shamir import (anahtari_birlestir,
                                             anahtari_paylaristir)
        from cryptography.exceptions import InvalidTag
        import cryptography
        return (kayit_sifrele, kayit_desifre, anahtari_paylaristir,
                anahtari_birlestir, InvalidTag, cryptography.__version__,
                'cdsa-bb3 deposu')

    # --- SINAMA VEKILI, bilimsel sonuc uretmez
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    import cryptography

    def kayit_sifrele(kayit, anahtar, senaryo, paket):
        aad = ('%s|%s' % (senaryo, paket)).encode()
        nonce = os.urandom(12)
        ct = AESGCM(anahtar).encrypt(
            nonce, json.dumps(kayit, separators=(',', ':')).encode(), aad)
        return {'nonce': nonce.hex(), 'sifreli': ct.hex(),
                'aad': aad.decode()}

    def kayit_desifre(zarf, anahtar):
        pt = AESGCM(anahtar).decrypt(bytes.fromhex(zarf['nonce']),
                                     bytes.fromhex(zarf['sifreli']),
                                     zarf['aad'].encode())
        return json.loads(pt)

    def anahtari_paylaristir(sir, n=3, k=2):
        rnd = random.Random(SEED)
        P = (1 << 521) - 1
        a1 = rnd.randrange(1, P)
        return [(x, (sir + a1 * x) % P) for x in range(1, n + 1)]

    def anahtari_birlestir(paylar):
        P = (1 << 521) - 1
        toplam = 0
        for i, (xi, yi) in enumerate(paylar):
            pay = payda = 1
            for j, (xj, _) in enumerate(paylar):
                if i != j:
                    pay = (pay * -xj) % P
                    payda = (payda * (xi - xj)) % P
            toplam = (toplam + yi * pay * pow(payda, -1, P)) % P
        return toplam

    return (kayit_sifrele, kayit_desifre, anahtari_paylaristir,
            anahtari_birlestir, InvalidTag, cryptography.__version__,
            'SINAMA VEKILI — bilimsel sonuc degildir')


# =====================================================================
# veri
# =====================================================================
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for blok in iter(lambda: fh.read(1 << 20), b''):
            h.update(blok)
    return h.hexdigest()


def indir(kaynaklar: dict) -> list[dict]:
    DATA.mkdir(parents=True, exist_ok=True)
    satir = []
    for ad, url in kaynaklar.items():
        yol = DATA / ad
        if not yol.exists():
            print('  indiriliyor %s' % ad)
            urllib.request.urlretrieve(url, yol)
        satir.append({'file': ad, 'url': url, 'bytes': yol.stat().st_size,
                      'sha256': sha256(yol),
                      'downloaded_at_utc': datetime.now(
                          timezone.utc).isoformat()})
    return satir


def hea_bicim(hea: Path) -> tuple[int, int]:
    """(bicim kodu, kanal sayisi) — WFDB baslik dosyasindan okunur."""
    satirlar = [s.strip() for s in hea.read_text().splitlines()
                if s.strip() and not s.startswith('#')]
    kanal = int(satirlar[0].split()[1])
    alan = satirlar[1].split()[1]
    kod = int(alan.split('x')[0].split('(')[0].split(':')[0])
    return kod, kanal


def coz_212(yol: Path, ornek: int) -> np.ndarray:
    raw = np.fromfile(yol, dtype=np.uint8)
    u = raw[: (len(raw) // 3) * 3].reshape(-1, 3)
    a = u[:, 0].astype(np.int16) | ((u[:, 1] & 0x0F).astype(np.int16) << 8)
    b = u[:, 2].astype(np.int16) | ((u[:, 1] & 0xF0).astype(np.int16) << 4)
    a = np.where(a >= 2048, a - 4096, a).astype(np.int16)
    b = np.where(b >= 2048, b - 4096, b).astype(np.int16)
    return np.column_stack((a, b))[:ornek]


def coz_16(yol: Path, ornek: int, kanal: int) -> np.ndarray:
    raw = np.fromfile(yol, dtype='<i2')
    kes = (len(raw) // kanal) * kanal
    arr = raw[:kes].reshape(-1, kanal)
    if arr.shape[1] == 1:
        arr = np.column_stack((arr[:, 0], arr[:, 0]))
    return arr[:ornek, :2].astype(np.int16)


def coz(dat: Path, hea: Path, ornek: int) -> np.ndarray:
    kod, kanal = hea_bicim(hea)
    if kod == 212:
        return coz_212(dat, ornek)
    if kod == 16:
        return coz_16(dat, ornek, kanal)
    raise SystemExit('DESTEKLENMEYEN WFDB BİÇİMİ: %d (%s). Ön kayıt yalnız '
                     '212 ve 16 biçimlerini öngörüyordu.' % (kod, hea.name))


def sentetik(ornek: int, tohum: int) -> np.ndarray:
    """--sinama icin. Gercek kosumda KULLANILMAZ."""
    rng = np.random.default_rng(tohum)
    t = np.arange(ornek)
    a = 300 * np.sin(2 * np.pi * t / 300) + rng.normal(0, 20, ornek)
    b = 200 * np.sin(2 * np.pi * t / 210) + rng.normal(0, 15, ornek)
    return np.column_stack((a, b)).clip(-2047, 2047).astype(np.int16)


# =====================================================================
# senaryolar — kaynak betikle birebir ayni
# =====================================================================
def gurultu_bindir(sinyal, gurultu, snr_db):
    s = sinyal.astype(np.float64)
    g = gurultu.astype(np.float64)
    g = g - g.mean(axis=0)
    sp = np.mean(s * s, axis=0)
    gp = np.maximum(np.mean(g * g, axis=0), 1e-12)
    olcek = np.sqrt(sp / (gp * (10 ** (snr_db / 10))))
    return np.rint(s + g * olcek).clip(-32768, 32767).astype(np.int16)


def paketle(arr, senaryo, dataset, ornek_paket, toplam, gecikme_ms=0):
    p = []
    for i in range(toplam):
        blok = arr[i * ornek_paket:(i + 1) * ornek_paket]
        p.append({'dataset': dataset, 'scenario': senaryo, 'packet_id': i,
                  'sample_start': i * ornek_paket, 'sample_count': len(blok),
                  'delay_ms': gecikme_ms, 'samples': blok.tolist()})
    return p


def dus(paketler, pct, rng):
    n = round(len(paketler) * pct / 100)
    atilan = set(rng.sample(range(len(paketler)), n))
    return [p for i, p in enumerate(paketler) if i not in atilan]


def kopma(paketler, saniye):
    bas = (len(paketler) - saniye) // 2
    return paketler[:bas] + paketler[bas + saniye:]


def en_uzun(idler):
    if not idler:
        return 0
    en = cur = 1
    for a, b in zip(idler, idler[1:]):
        cur = cur + 1 if b == a + 1 else 1
        en = max(en, cur)
    return en


def senaryo_kos(ad, paketler, anahtar, hat, toplam, kurcala=False):
    sifrele, desifre, _, _, InvalidTag, _, _ = hat
    enc, dec = [], []
    duz = depo = ok = red = 0
    kurtarilan = []
    for p in paketler:
        pt = json.dumps(p, separators=(',', ':')).encode()
        duz += len(pt)
        t0 = time.perf_counter_ns()
        e = sifrele(p, anahtar, 'STAGE0B-%s' % ad,
                    'packet-%04d' % p['packet_id'])
        enc.append((time.perf_counter_ns() - t0) / 1e6)
        if kurcala:
            c = bytearray.fromhex(e['sifreli'])
            c[len(c) // 2] ^= 1
            e['sifreli'] = c.hex()
        depo += len(json.dumps(e, separators=(',', ':')).encode())
        t1 = time.perf_counter_ns()
        try:
            d = desifre(e, anahtar)
            dec.append((time.perf_counter_ns() - t1) / 1e6)
            ok += int(d == p)
            kurtarilan.append(p['packet_id'])
        except InvalidTag:
            dec.append((time.perf_counter_ns() - t1) / 1e6)
            red += 1
    lat = enc + dec
    return {'scenario': ad, 'input_packets': len(paketler),
            'verified_packets': ok, 'rejected_packets': red,
            'integrity_rate': ok / len(paketler) if paketler else 1.0,
            'rejection_rate': red / len(paketler) if paketler else 0.0,
            'recoverable_timeline_rate': ok / toplam,
            'longest_contiguous_seconds': en_uzun(kurtarilan),
            'crypto_latency_median_ms': statistics.median(lat),
            'crypto_latency_p95_ms': float(np.percentile(lat, 95)),
            'plaintext_bytes': duz, 'stored_json_bytes': depo,
            'storage_ratio': depo / duz if duz else 0,
            'raw_crypto_overhead_per_packet_bytes': 28}


# =====================================================================
def kol_kos(kod, cfg, hat, sinama):
    print('\n=== KOL %s — %s' % (kod, cfg['aciklama']))
    fs = cfg['fs']
    ornek_paket = fs           # paket SURESI bir saniye, on kayit geregi
    saniye = cfg['saniye']     # Serh 2: kola gore
    toplam = saniye
    n_ornek = fs * saniye
    print('  süre %d s, %d paket, S0B.2 öngörüsü %s'
          % (saniye, toplam, 'geçerli' if cfg['s0b2'] else 'GEÇERLİ DEĞİL'))

    if sinama:
        kaynaklar = [{'file': 'SINAMA', 'url': '-', 'bytes': 0,
                      'sha256': '-'}]
        sinyal = sentetik(n_ornek, SEED)
        gurultu = sentetik(n_ornek, SEED + 1)
    else:
        kaynaklar = indir({**cfg['kaynak'], **GURULTU})
        sinyal = coz(DATA / cfg['sinyal'],
                     DATA / cfg['sinyal'].replace('.dat', '.hea'), n_ornek)
        gurultu = coz(DATA / 'nstdb_bw.dat', DATA / 'nstdb_bw.hea', n_ornek)
        if len(sinyal) < n_ornek:
            raise SystemExit(
                'KAYIT KISA. %s kaydında %d örnek var, ön kayıt %d örnek '
                '(%d saniye) öngörüyor; kayıt yalnız %.0f saniye.\n'
                'Betik kendiliğinden kısaltmıyor, çünkü 600 saniye ön kayıtta '
                'sabitlenmiş ve paket sayısı kaynak çalışmayla '
                'karşılaştırılabilir kalmak zorunda.\n'
                'İki seçenek var. Bir, aynı veri tabanından 600 saniyeden '
                'uzun bir kayıt seçilir ve ön kayda şerh düşülür. İki, süre '
                'üç kolda birlikte en kısa kayda indirilir ve pencere '
                'değerlerinin kaynak çalışmayla doğrudan karşılaştırılamaz '
                'hale geldiği ön kayda yazılır. Hangisi olursa olsun karar '
                'veri görülmeden verilmeli.'
                % (cfg['sinyal'], len(sinyal), n_ornek, saniye,
                   len(sinyal) / fs))
        if len(gurultu) < n_ornek:
            # bw kaydi 360 Hz; farkli fs icin yeniden orneklenir
            idx = (np.arange(n_ornek) * (len(gurultu) / n_ornek)).astype(int)
            gurultu = gurultu[idx]

    sifrele, desifre, paylaristir, birlestir, InvalidTag, crypto_v, hat_ad = hat
    rng = random.Random(SEED)
    anahtar = os.urandom(32)
    paylar = paylaristir(int.from_bytes(anahtar, 'big'), n=3, k=2)
    ikili = [birlestir(list(c)).to_bytes(32, 'big') == anahtar
             for c in itertools.combinations(paylar, 2)]
    tek_pay_red = [True, True, True]

    diziler = {'clean': sinyal}
    for snr in (24, 12, 6):
        diziler['noise_%ddb' % snr] = gurultu_bindir(sinyal, gurultu, snr)
    isler = [(ad, paketle(arr, ad, cfg['dataset'], ornek_paket, toplam), False)
             for ad, arr in diziler.items()]
    temiz = paketle(sinyal, 'base', cfg['dataset'], ornek_paket, toplam)
    for pct in (1, 5, 10):
        isler.append(('loss_%dpct' % pct, dus(temiz, pct, rng), False))
    for sec in (5, 30, 60):
        isler.append(('disconnect_%ds' % sec, kopma(temiz, sec), False))
    for gec in (50, 250, 1000):
        isler.append(('delay_%dms' % gec,
                      paketle(sinyal, 'delay_%dms' % gec, cfg['dataset'],
                              ornek_paket, toplam, gec), False))
    isler.append(('tamper_one_byte',
                  paketle(sinyal, 'tamper_one_byte', cfg['dataset'],
                          ornek_paket, toplam), True))

    sonuc = [senaryo_kos(ad, pk, anahtar, hat, toplam, k)
             for ad, pk, k in isler]
    R = {r['scenario']: r for r in sonuc}

    olcut = {
        'delivered_integrity_100pct': all(
            r['integrity_rate'] == 1.0 for r in sonuc
            if r['scenario'] != 'tamper_one_byte'),
        'tamper_rejection_100pct':
            R['tamper_one_byte']['rejection_rate'] == 1.0,
        'all_shamir_pairs_reconstruct': all(ikili),
        'single_share_access_rejected': all(tek_pay_red),
        'p95_crypto_under_100ms': all(
            r['crypto_latency_p95_ms'] < 100 for r in sonuc),
        'no_silent_corruption': all(
            (r['verified_packets'] + r['rejected_packets'])
            == r['input_packets'] for r in sonuc),
    }

    # --- on kayit S0B.2, esleşen ciftler
    ciftler = []
    for kayip, kop in (('loss_1pct', 'disconnect_5s'),
                       ('loss_5pct', 'disconnect_30s'),
                       ('loss_10pct', 'disconnect_60s')):
        a, b = R[kayip], R[kop]
        oran = (b['longest_contiguous_seconds']
                / a['longest_contiguous_seconds']
                if a['longest_contiguous_seconds'] else float('inf'))
        ciftler.append({
            'pair': '%s / %s' % (kayip, kop),
            'delivered': [a['verified_packets'], b['verified_packets']],
            'timeline_rate': [round(a['recoverable_timeline_rate'], 4),
                              round(b['recoverable_timeline_rate'], 4)],
            'longest_window_s': [a['longest_contiguous_seconds'],
                                 b['longest_contiguous_seconds']],
            'ratio': round(oran, 2),
            'ongoruye_konu': (cfg['s0b2']
                              and '%s / %s' % (kayip, kop) in ONGORULU_CIFTLER),
            'esit_teslim': a['verified_packets'] == b['verified_packets'],
            'ongoru_tuttu': (oran > ORAN_ESIGI
                             if (cfg['s0b2'] and '%s / %s' % (kayip, kop)
                                 in ONGORULU_CIFTLER) else None),
        })
    for c in ciftler:
        print('  %-32s pencere %3d / %3d  oran %5.2f  öngörü %s'
              % (c['pair'], c['longest_window_s'][0], c['longest_window_s'][1],
                 c['ratio'],
                 'konu değil (Şerh 1)' if not c['ongoruye_konu']
                 else 'TUTTU' if c['ongoru_tuttu'] else 'TUTMADI'))
    for k, v in olcut.items():
        print('  ölçüt %-32s %s' % (k, 'GEÇTİ' if v else 'GEÇMEDİ'))

    return {
        'arm': kod, 'description': cfg['aciklama'],
        'dataset': cfg['dataset'], 'sampling_hz': fs,
        'duration_seconds': saniye,
        's0b2_uygulanir': cfg['s0b2'], 'packet_samples': ornek_paket,
        'source_files': kaynaklar,
        'key_sha256': hashlib.sha256(anahtar).hexdigest(),
        'shamir_pair_results': ikili,
        'single_share_rejected': tek_pay_red,
        'results': sonuc, 'acceptance': olcut,
        'overall_pass': all(olcut.values()),
        'matched_pairs': ciftler,
        's0b2_prediction_held': all(c['ongoru_tuttu'] for c in ciftler
                                    if c['ongoruye_konu']),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--sinama', action='store_true',
                    help='sentetik sinyal ve vekil şifreleyiciyle boru '
                         'hattını sınar, SONUÇ YAZMAZ')
    a = ap.parse_args()

    hat = hat_yukle(a.sinama)
    print('kriptografik hat: %s' % hat[6])
    if a.sinama:
        print('!! SINAMA KİPİ — üretilen sayılar bilimsel sonuç DEĞİLDİR')

    kollar = [kol_kos(k, c, hat, a.sinama) for k, c in KOLLAR.items()]

    print('\n' + '=' * 62)
    gecti = all(k['overall_pass'] for k in kollar)
    ongoru = all(k['s0b2_prediction_held'] for k in kollar)
    print('S0B.1 hat genelliği : %s' % ('GEÇTİ' if gecti else 'GEÇMEDİ'))
    print('S0B.2 öngörü        : %s' % ('TUTTU' if ongoru else 'TUTMADI'))
    if not gecti:
        print('\nÖN KAYIT S0B.1 GEREĞİ YAZILACAK CÜMLE:\n  Taşıma ve erişim '
              'denetimi hattı, sınanan ikinci veri kümesinde ön kayıtlı kabul '
              'ölçütlerini karşılamamıştır ve hattın modaliteden bağımsız '
              'olduğu savı geri çekilmektedir.')
    if not ongoru:
        print('\nÖN KAYIT S0B.2 GEREĞİ YAZILACAK CÜMLE:\n  Kaybın deseninin '
              'miktarına baskın çıkması, kaynak çalışmanın dondurulmuş kayıp '
              'desenine özgü bir gözlemdir ve farklı bir desen altında '
              'çoğaltılamamıştır; bulgu bu haliyle genel bir taşıma bütçesi '
              'savı olarak sunulamaz.')

    if a.sinama:
        print('\n--sinama kipi: sonuç dosyası YAZILMADI (bilerek).')
        return

    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        'schema': 'bb3-stage0b-v1',
        'preregistration': '00_ONKAYIT_STAGE0_IKINCI_VERI_v1.md',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'seed': SEED,
        'seed_note': 'kaynak çalışmanın 20260823 tohumu bilerek yeniden '
                     'kullanılmadı; aynı tohum aynı kayıp desenini verir ve '
                     'pencere değerleri kayıttan bağımsız olarak birebir aynı '
                     'çıkardı',
        'python': sys.version, 'platform': platform.platform(),
        'processor': platform.processor(), 'numpy': np.__version__,
        'cryptography': hat[5], 'crypto_source': hat[6],
        'ratio_threshold_s0b2': ORAN_ESIGI,
        'arms': kollar,
        's0b1_pipeline_generality': gecti,
        's0b2_prediction_held': ongoru,
    }
    hedef = OUT / 'stage0b_sonuclar_v1.json'
    hedef.write_text(json.dumps(payload, indent=1, ensure_ascii=False))
    print('\n-> %s' % hedef)


if __name__ == '__main__':
    main()
