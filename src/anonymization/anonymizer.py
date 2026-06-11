"""
Module 2 — Anonymization
=========================

Two-layer anonymization for synthetic biometric records:
    1. k-Anonymity (k=5) on (route, shift) quasi-identifier combinations
    2. Laplace differential privacy on numeric fields (epsilon=1.0)

Reference (Dwork & Roth, 2014):
    M(x) = x + Lap(Delta_f / epsilon)

Sensitivity values (thesis Annex B Table 7):
    HRV   Delta_f = 5.0 ms
    SpO2  Delta_f = 1.0 %
    GSR   Delta_f = 2.0 uS
    SRS   Delta_f = 0.05
"""

from collections import Counter

import numpy as np


def laplace_gurultu_ekle(deger: float, duyarlilik: float, epsilon: float) -> float:
    """
    Add Laplace noise to a numeric value for differential privacy.

    Parameters
    ----------
    deger : float
        Raw measurement value.
    duyarlilik : float
        Sensitivity Delta_f (maximum query change for one record).
    epsilon : float
        Privacy budget (epsilon=1.0 used in the thesis).

    Returns
    -------
    float — value with Laplace noise added, rounded to 3 decimals.
    """
    scale = duyarlilik / epsilon
    gurultu = float(np.random.laplace(loc=0.0, scale=scale))
    return round(deger + gurultu, 3)


def anonimize_et(kayitlar: list, k: int = 5, epsilon: float = 1.0) -> list:
    """
    Apply two-layer anonymization to a list of biometric records.

    Step 1 — k-Anonymity (k=5):
        Records whose (route, shift) combination has fewer than k members
        are excluded from the output.
    Step 2 — Laplace differential privacy (epsilon=1.0):
        Independent Laplace noise is added to HRV, SpO2, GSR, SRS.

    Parameters
    ----------
    kayitlar : list of dict
        Output of synthetic_data.generator.veri_uret().
    k : int
        Minimum group size for k-anonymity (default: 5).
    epsilon : float
        Differential-privacy budget (default: 1.0).

    Returns
    -------
    list of dict — anonymized records.
    """
    kombinasyonlar = Counter((kayit["rota"], kayit["vardiya"]) for kayit in kayitlar)
    gecerli = {combo for combo, n in kombinasyonlar.items() if n >= k}

    sonuc = []
    for kayit in kayitlar:
        if (kayit["rota"], kayit["vardiya"]) not in gecerli:
            continue
        sonuc.append({
            "rota":    kayit["rota"],
            "vardiya": kayit["vardiya"],
            "hrv":  laplace_gurultu_ekle(kayit["hrv"],  5.0,  epsilon),
            "spo2": laplace_gurultu_ekle(kayit["spo2"], 1.0,  epsilon),
            "gsr":  laplace_gurultu_ekle(kayit["gsr"],  2.0,  epsilon),
            "srs":  laplace_gurultu_ekle(kayit["srs"],  0.05, epsilon),
        })
    return sonuc
