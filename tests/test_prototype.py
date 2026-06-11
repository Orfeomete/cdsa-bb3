"""
Test suite for the CDSA-Blackbox prototype.

Run with:
    pytest tests/

Five tests cover determinism of the generator, statistical sanity of
the validation report, k-anonymity invariance, AES-GCM tamper detection,
and Shamir 2-of-3 reconstruction.
"""

import os
import sys

import pytest

# Make `src` importable when running pytest from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.synthetic_data.generator import veri_uret, istatistiksel_dogrulama
from src.anonymization.anonymizer import anonimize_et
from src.cryptography.aes_gcm import kayit_sifrele, kayit_desifre
from src.cryptography.shamir import anahtari_paylaristir, anahtari_birlestir


def test_generator_deterministic():
    """Same seed must produce identical output across calls."""
    a = veri_uret(seed=42)
    b = veri_uret(seed=42)
    assert a == b
    assert len(a) == 1179


def test_validation_report_signs():
    """Spearman rho should be strongly negative; Night SRS > Day SRS."""
    rapor = istatistiksel_dogrulama(veri_uret(seed=42))
    assert rapor["spearman"]["rho"] < -0.5
    assert rapor["spearman"]["p"] < 1e-3
    assert rapor["mannwhitney"]["gece_mean"] > rapor["mannwhitney"]["gunduz_mean"]
    assert rapor["mannwhitney"]["p"] < 1e-3


def test_kanonymity_retains_all():
    """With the standard calibration matrix, every subgroup has n >= 5."""
    kayitlar = veri_uret(seed=42)
    anon = anonimize_et(kayitlar, k=5, epsilon=1.0)
    assert len(anon) == len(kayitlar)


def test_aes_gcm_tamper_detection():
    """A flipped bit in the ciphertext must trigger an InvalidTag exception."""
    from cryptography.exceptions import InvalidTag
    key = os.urandom(32)
    payload = {"hrv": 33.2, "spo2": 96.4}
    sif = kayit_sifrele(payload, key, "TC-XXX-2026042", "2026-04-18T03:42:00Z")
    # Flip one nibble of the ciphertext
    tampered = sif.copy()
    head = bytes.fromhex(tampered["sifreli"])
    head = bytearray(head)
    head[0] ^= 0x01
    tampered["sifreli"] = head.hex()
    with pytest.raises(InvalidTag):
        kayit_desifre(tampered, key)


def test_shamir_2_of_3_reconstruction():
    """Any 2 of 3 shares must reconstruct the secret; 1 share must not."""
    secret = int.from_bytes(os.urandom(32), "big")
    shares = anahtari_paylaristir(secret, n=3, k=2)

    # Each pair of shares reconstructs the original secret
    pairs = [(shares[0], shares[1]), (shares[0], shares[2]), (shares[1], shares[2])]
    for pair in pairs:
        assert anahtari_birlestir(list(pair)) == secret

    # A single share is incomplete; "reconstruction" returns share's own y-value
    # (i.e. it does not equal the secret with overwhelming probability)
    single = anahtari_birlestir([shares[0]])
    assert single != secret
