"""The sharing coefficient must be drawn from the whole field GF(p), not from 256 bits (fixed in v2.3.0)."""
import os
from src.cryptography.shamir import P, anahtari_paylaristir, anahtari_birlestir


def test_coefficient_reaches_upper_half_of_field():
    # With a uniform coefficient on GF(p), p > 2**256, about half of the draws exceed 2**256.
    # The chance that 64 uniform draws all stay below 2**256 is about 2**-64.
    buyuk = 0
    for _ in range(64):
        anahtar = int.from_bytes(os.urandom(32), "big")
        (x1, y1), _, _ = anahtari_paylaristir(anahtar, n=3, k=2)
        a1 = (y1 - anahtar) * pow(x1, P - 2, P) % P
        buyuk += a1 >= 2**256
    assert buyuk > 0


def test_pairs_still_reconstruct():
    import itertools
    for _ in range(20):
        anahtar = int.from_bytes(os.urandom(32), "big")
        paylar = anahtari_paylaristir(anahtar, n=3, k=2)
        for ikili in itertools.combinations(paylar, 2):
            assert anahtari_birlestir(list(ikili)) == anahtar
