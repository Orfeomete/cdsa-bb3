"""Aşama 0 kayıp deseni için keşifsel model (ön kayıtlı değil, sonuçlar bilindikten sonra yazıldı).

1. Dağınık kayıp. Aşama 0 betiği N paketten round(N*yüzde/100) paketi yerine koymadan rastgele siler
   (stage0_kosum_v1.drop_packets). En uzun teslim dizisinin dağılımı benzetimle ve iki yaklaşık
   formülle hesaplanır, 2000 tohumluk taramanın ortancalarıyla karşılaştırılır.
2. Gilbert-Elliott kanalı. İyi durumda kayıp yok, kötü durumda her paket kaybolur. Ortalama patlama
   uzunluğu B paket, durağan kayıp oranı L. Belirli bir W paketlik pencerenin (olay öncesi pencere)
   eksiksiz gelme olasılığı analitik olarak ve benzetimle hesaplanır.
3. Tasarım kuralı. Pencerenin 1-delta olasılıkla eksiksiz gelmesi için izin verilen en büyük L.

Çıktı patlamali_kayip_modeli.json. Tohum 20261014.
"""
import json, math, random, sys
import numpy as np

TOHUM = 20261014
rng = np.random.default_rng(TOHUM)


# ------------------------------------------------------------------ 0. asal denetimi
def miller_rabin(n, turlar=64, tohum=TOHUM):
    if n < 2:
        return False
    kucuk = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for q in kucuk:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    r = random.Random(tohum)
    tabanlar = kucuk + [r.randrange(2, n - 2) for _ in range(turlar)]
    for a in tabanlar:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


P = 2 ** 257 - 93
asal = miller_rabin(P)
# 2^257 - 93'ün 2^257'nin altındaki en büyük asal olup olmadığı (93'ten küçük çıkarımlar bileşik mi)
daha_buyuk_asal_yok = all(not miller_rabin(2 ** 257 - k) for k in range(1, 93, 2))


# ------------------------------------------------------------------ 1. dağınık kayıp
def en_uzun_dizi(teslim):
    """teslim: bool dizisi. En uzun True dizisi."""
    en = cur = 0
    for t in teslim:
        cur = cur + 1 if t else 0
        en = max(en, cur)
    return en


def dagik_benzetim(N, K, tekrar):
    sonuc = np.empty(tekrar, dtype=np.int32)
    for i in range(tekrar):
        kayip = np.sort(rng.choice(N, size=K, replace=False))
        sinir = np.concatenate(([-1], kayip, [N]))
        sonuc[i] = int(np.max(np.diff(sinir) - 1))
    return sonuc


def harmonik(n):
    return sum(1.0 / k for k in range(1, n + 1))


dagik = {}
TARAMA_ORTANCA = {1: 298 / 1.42, 5: 285 / 3.96, 10: 270 / 6.59}   # 2000 tohum, oran ortancasından
DONDURULMUS = {1: 199, 5: 74, 10: 40}
for yuzde in (1, 5, 10):
    N = 600
    K = round(N * yuzde / 100)
    L = K / N
    s = dagik_benzetim(N, K, 100000)
    M = N - K
    aralik_beklenen = M / (K + 1) * harmonik(K + 1)              # rastgele aralıkların en büyüğü
    erdos_renyi = math.log(N * L) / -math.log(1 - L)             # en uzun başarı dizisi, öncü terim
    dagik[f'{yuzde}%'] = dict(
        N=N, K=K, benzetim_ortalama=float(s.mean()), benzetim_ortanca=float(np.median(s)),
        benzetim_p05=float(np.percentile(s, 5)), benzetim_p95=float(np.percentile(s, 95)),
        aralik_formulu=aralik_beklenen, erdos_renyi_oncu=erdos_renyi,
        tarama_ortanca_yaklasik=TARAMA_ORTANCA[yuzde], dondurulmus_tohum=DONDURULMUS[yuzde])


# kayıt süresiyle büyüme (bir saatlik kayıt, 3600 paket)
uzun_kayit = {}
for yuzde in (1, 5, 10):
    N = 3600
    K = round(N * yuzde / 100)
    s = dagik_benzetim(N, K, 20000)
    uzun_kayit[f'{yuzde}%'] = dict(N=N, K=K, aralik_formulu=(N - K) / (K + 1) * harmonik(K + 1),
                                    benzetim_ortalama=float(s.mean()), benzetim_ortanca=float(np.median(s)))


# ------------------------------------------------------------------ 2. Gilbert-Elliott pencere olasılığı
def ge_parametre(L, B):
    r = 1.0 / B                       # kötüden iyiye geçiş
    p = L * r / (1.0 - L)             # iyiden kötüye geçiş, durağan kayıp L = p / (p + r)
    return p, r


def pencere_analitik(L, B, W):
    p, _ = ge_parametre(L, B)
    return (1.0 - L) * (1.0 - p) ** (W - 1)


def pencere_benzetim(L, B, W, tekrar):
    p, r = ge_parametre(L, B)
    # durağan dağılımdan başla, W adım yürü, hiç kötü durum görülmezse pencere eksiksiz
    kotu = rng.random(tekrar) < L
    saglam = ~kotu
    for _ in range(W - 1):
        u = rng.random(tekrar)
        kotu = np.where(kotu, u >= r, u < p)
        saglam &= ~kotu
    return float(saglam.mean())


ge = []
for L, B, W in [(0.01, 1, 60), (0.01, 10, 60), (0.01, 60, 60), (0.001, 1, 300), (0.001, 10, 300),
                (0.001, 60, 300), (0.005, 60, 300), (0.0002, 1, 300)]:
    ge.append(dict(L=L, B=B, W=W, analitik=pencere_analitik(L, B, W),
                   benzetim=pencere_benzetim(L, B, W, 200000)))


# ------------------------------------------------------------------ 3. tasarım kuralı
def izinli_L(W, B, delta):
    """(1-L)(1-p)^(W-1) = 1-delta denklemini L için ikiye bölmeyle çözer."""
    lo, hi = 0.0, 0.5
    for _ in range(200):
        orta = (lo + hi) / 2
        if pencere_analitik(orta, B, W) >= 1 - delta:
            lo = orta
        else:
            hi = orta
    return lo


kural = []
for W in (60, 300):
    for B in (1, 10, 60):
        Lx = izinli_L(W, B, 0.05)
        yaklasik = 0.05 * B / (B + W - 1)
        kural.append(dict(W=W, B=B, delta=0.05, izinli_L=Lx, yaklasik_dB_bolu_B_arti_W_eksi_1=yaklasik,
                          benzetim_pencere_olasiligi=pencere_benzetim(Lx, B, W, 200000)))

cikti = dict(tohum=TOHUM, onkayitli=False, not_='Sonuçlar bilindikten sonra yazılmış keşifsel çözümleme.',
             asal=dict(p='2^257-93', miller_rabin_asal=asal, tur=64 + 12,
                       arada_baska_asal_yok=daha_buyuk_asal_yok),
             dagik_kayip=dagik, bir_saatlik_kayit=uzun_kayit, gilbert_elliott_pencere=ge, tasarim_kurali=kural)
json.dump(cikti, open(sys.argv[1] if len(sys.argv) > 1 else 'patlamali_kayip_modeli.json', 'w'),
          ensure_ascii=False, indent=1)
print(json.dumps(cikti, ensure_ascii=False, indent=1))
