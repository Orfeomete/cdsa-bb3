"""
Reproduce the simulation results reported in thesis Section 4.1.6.

Outputs match `data/synthetic_n1179.json` byte-for-byte when run with
NumPy >= 1.24 (Mersenne Twister stream is stable across NumPy
versions on the canonical seed=42 path).
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.synthetic_data.generator import veri_uret, istatistiksel_dogrulama
from src.anonymization.anonymizer import anonimize_et


def main() -> int:
    repo = os.path.join(os.path.dirname(__file__), "..")
    os.makedirs(os.path.join(repo, "data"), exist_ok=True)

    print("Section 4.1.6 — synthetic data generation + validation")
    print("=" * 60)

    kayitlar = veri_uret(seed=42)
    print(f"Generated {len(kayitlar)} records over {len({k['rota'] for k in kayitlar})} routes "
          f"and {len({k['vardiya'] for k in kayitlar})} shift types")

    rapor = istatistiksel_dogrulama(kayitlar)

    print("\nStatistical validation")
    print(f"  Shapiro-Wilk normality   {rapor['normality']['passed']}/{rapor['normality']['total']} "
          f"subgroups pass (p > 0.05)")
    _sp = rapor['spearman']['p']
    _sp_str = '< 0.001' if _sp < 1e-3 else f'= {_sp:.4f}'
    print(f"  Spearman rho(HRV,GSR)  = {rapor['spearman']['rho']:+.4f}  "
          f"(p {_sp_str})")
    _mw = rapor['mannwhitney']['p']
    _mw_str = '< 0.001' if _mw < 1e-3 else f'= {_mw:.4f}'
    print(f"  Mann-Whitney U Night > Day SRS  "
          f"(p {_mw_str})")
    print(f"    Night mean = {rapor['mannwhitney']['gece_mean']:.4f}")
    print(f"    Day   mean = {rapor['mannwhitney']['gunduz_mean']:.4f}")

    anon = anonimize_et(kayitlar, k=5, epsilon=1.0)
    print(f"\nAnonymization (k=5, eps=1.0): {len(anon)} records retained")

    with open(os.path.join(repo, "data", "synthetic_n1179.json"), "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, indent=2, ensure_ascii=False)
    with open(os.path.join(repo, "data", "synthetic_n1179_anon.json"), "w", encoding="utf-8") as f:
        json.dump(anon, f, indent=2, ensure_ascii=False)
    with open(os.path.join(repo, "data", "statistical_validation_report.json"), "w", encoding="utf-8") as f:
        json.dump(rapor, f, indent=2)

    print("\nWrote:")
    print("  data/synthetic_n1179.json")
    print("  data/synthetic_n1179_anon.json")
    print("  data/statistical_validation_report.json")
    print("\nReproduction complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
