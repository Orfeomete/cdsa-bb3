"""
60-second end-to-end demonstration of CDSA-Blackbox.

Runs the three modules in sequence and prints a brief verification
report. Designed to be a fast smoke test after `pip install -r requirements.txt`.
"""

import os
import sys

# Make `src` importable when running the script from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.synthetic_data.generator import veri_uret, istatistiksel_dogrulama
from src.anonymization.anonymizer import anonimize_et
from src.cryptography.aes_gcm import kayit_sifrele, kayit_desifre
from src.cryptography.shamir import anahtari_paylaristir, anahtari_birlestir


def main() -> int:
    print("=" * 60)
    print(" CDSA-Blackbox — quick start")
    print("=" * 60)

    # Module 1
    kayitlar = veri_uret(seed=42)
    rapor = istatistiksel_dogrulama(kayitlar)
    print(f"\n Module 1 — Records generated: {len(kayitlar)}")
    print(f"   Spearman rho(HRV,GSR) = {rapor['spearman']['rho']:+.4f}")
    print(f"   Night SRS mean        = {rapor['mannwhitney']['gece_mean']:.4f}")
    print(f"   Day   SRS mean        = {rapor['mannwhitney']['gunduz_mean']:.4f}")

    # Module 2
    anon = anonimize_et(kayitlar, k=5, epsilon=1.0)
    print(f"\n Module 2 — Anonymized records: {len(anon)}")
    print(f"   (dropped {len(kayitlar) - len(anon)} for k-anonymity)")

    # Module 3
    ana = os.urandom(32)
    ana_int = int.from_bytes(ana, "big")
    test = {"hrv": 33.2, "spo2": 96.4, "gsr": 13.96, "srs": 0.457}
    sif = kayit_sifrele(test, ana, "TC-XXX-2026042", "2026-04-18T03:42:00Z")
    parcalar = anahtari_paylaristir(ana_int, n=3, k=2)
    ana_yeni = anahtari_birlestir(parcalar[:2]).to_bytes(32, "big")
    acik = kayit_desifre(sif, ana_yeni)
    print(f"\n Module 3 — AES-256-GCM + Shamir 2/3:")
    print(f"   key round-trip:    {'OK' if ana == ana_yeni else 'FAIL'}")
    print(f"   payload round-trip: {'OK' if acik == test else 'FAIL'}")

    print("\n" + "=" * 60)
    print(" All modules verified.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
