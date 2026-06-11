"""
Module 1 — Synthetic Biometric Data Generation + Statistical Validation
========================================================================

Thesis: CDSA — Complementary Diagnostic Safety Approach
Section 4.2.1 — Route × Shift Calibration Matrix (Annex B Table 3)

Generates n=1179 synthetic biometric records aligned with eight long-haul
routes flown from Istanbul (IST-SYD, GRU, NRT, ORD, SIN, JFK, LHR, DXB)
and two shift types (Night / Day). Each record carries HRV (ms), SpO2 (%),
GSR (uS), and the derived Stress-Recovery Score (SRS, 0-1).

The model parameters are documented in thesis Annex B Table 3.
Determinism: numpy.random.seed(42) — byte-reproducible across runs.

Statistical validation: Shapiro-Wilk (subgroup normality), Spearman
(HRV ~ GSR inverse correlation), Mann-Whitney U (Night > Day SRS).
"""

import numpy as np
from scipy import stats


# Route parameters (Section 4.2.3, Table 3)
# Mean SRS per (route, shift); n_gece / n_gunduz = sample counts.
ROTALAR = {
    "IST-SYD": {"gece_srs": 0.440, "gunduz_srs": 0.286, "n_gece": 128, "n_gunduz": 25},
    "IST-GRU": {"gece_srs": 0.214, "gunduz_srs": 0.095, "n_gece":  65, "n_gunduz": 62},
    "IST-NRT": {"gece_srs": 0.177, "gunduz_srs": 0.076, "n_gece": 108, "n_gunduz": 35},
    "IST-ORD": {"gece_srs": 0.165, "gunduz_srs": 0.052, "n_gece":  83, "n_gunduz": 75},
    "IST-SIN": {"gece_srs": 0.161, "gunduz_srs": 0.060, "n_gece": 105, "n_gunduz": 64},
    "IST-JFK": {"gece_srs": 0.153, "gunduz_srs": 0.051, "n_gece": 100, "n_gunduz": 52},
    "IST-LHR": {"gece_srs": 0.109, "gunduz_srs": 0.048, "n_gece":  44, "n_gunduz": 99},
    "IST-DXB": {"gece_srs": 0.101, "gunduz_srs": 0.048, "n_gece":  55, "n_gunduz": 79},
}


def veri_uret(seed: int = 42) -> list:
    """
    Generate n=1179 synthetic biometric records.

    Physiological generative model (Annex B Table 3):
        HRV  ~ N(65  - SRS * 95,  sigma=5.0),  clipped to [18,   78]   ms
        SpO2 ~ N(98.2 - SRS * 4.5, sigma=0.4), clipped to [91,   99.5] %
        GSR  ~ N(5   + SRS * 22,  sigma=1.8),  clipped to [3.2,  24.8] uS

    Returns
    -------
    list of dict
        Each dict has keys: rota, vardiya, hrv, spo2, gsr, srs.
    """
    np.random.seed(seed)

    kayitlar = []
    for rota, info in ROTALAR.items():
        for vardiya, n, srs_mu in [
            ("Gece",   info["n_gece"],   info["gece_srs"]),
            ("Gunduz", info["n_gunduz"], info["gunduz_srs"]),
        ]:
            srs  = np.clip(np.random.normal(srs_mu, 0.03, n), 0.02, 0.62)
            hrv  = np.clip(65   - srs * 95  + np.random.normal(0, 5.0, n), 18.0, 78.0)
            spo2 = np.clip(98.2 - srs * 4.5 + np.random.normal(0, 0.4, n), 91.0, 99.5)
            gsr  = np.clip(5    + srs * 22  + np.random.normal(0, 1.8, n),  3.2, 24.8)

            for i in range(n):
                kayitlar.append({
                    "rota": rota,
                    "vardiya": vardiya,
                    "hrv":  round(float(hrv[i]),  1),
                    "spo2": round(float(spo2[i]), 1),
                    "gsr":  round(float(gsr[i]),  2),
                    "srs":  round(float(srs[i]),  3),
                })
    return kayitlar


def istatistiksel_dogrulama(kayitlar: list) -> dict:
    """
    Validate the statistical properties of the synthetic dataset.

    Returns
    -------
    dict — report with three keys:
        normality:   {passed: int, total: int, ratio: float}
        spearman:    {rho: float, p: float, passes: bool}
        mannwhitney: {u: float, p: float, gece_mean: float, gunduz_mean: float, passes: bool}
    """
    hrv = np.array([k["hrv"] for k in kayitlar])
    gsr = np.array([k["gsr"] for k in kayitlar])

    # Test 1: Shapiro-Wilk normality per (route, shift) subgroup
    gecen, toplam = 0, 0
    for rota in set(k["rota"] for k in kayitlar):
        for vardiya in ["Gece", "Gunduz"]:
            alt_grup = [k for k in kayitlar if k["rota"] == rota and k["vardiya"] == vardiya]
            if len(alt_grup) < 3:
                continue
            ps = [
                stats.shapiro(np.array([k["hrv"]  for k in alt_grup]))[1],
                stats.shapiro(np.array([k["spo2"] for k in alt_grup]))[1],
                stats.shapiro(np.array([k["gsr"]  for k in alt_grup]))[1],
            ]
            if all(p > 0.05 for p in ps):
                gecen += 1
            toplam += 1

    # Test 2: Spearman correlation HRV ~ GSR (expected negative)
    rho, p_sp = stats.spearmanr(hrv, gsr)

    # Test 3: Mann-Whitney U — Night SRS > Day SRS (one-sided)
    srs_gece   = np.array([k["srs"] for k in kayitlar if k["vardiya"] == "Gece"])
    srs_gunduz = np.array([k["srs"] for k in kayitlar if k["vardiya"] == "Gunduz"])
    u, p_mw = stats.mannwhitneyu(srs_gece, srs_gunduz, alternative="greater")

    return {
        "normality": {
            "passed": gecen,
            "total":  toplam,
            "ratio":  round(gecen / toplam, 3) if toplam else 0.0,
        },
        "spearman": {
            "rho":    round(float(rho),  4),
            "p":      float(p_sp),
            "passes": bool(rho < -0.5),
        },
        "mannwhitney": {
            "u":           float(u),
            "p":           float(p_mw),
            "gece_mean":   round(float(srs_gece.mean()),   4),
            "gunduz_mean": round(float(srs_gunduz.mean()), 4),
            "passes":      bool(p_mw < 0.001),
        },
    }


if __name__ == "__main__":
    kayitlar = veri_uret(seed=42)
    print(f"{len(kayitlar)} synthetic records generated")
    rapor = istatistiksel_dogrulama(kayitlar)
    print("\nStatistical validation report:")
    for test_name, sonuc in rapor.items():
        print(f"  {test_name}: {sonuc}")
