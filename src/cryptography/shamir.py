"""
Module 3.2 — Shamir Secret Sharing (n/k Threshold Scheme)
==========================================================

Splits an AES master key into n shares such that any k of them can
reconstruct the key via Lagrange interpolation over the finite field
GF(p), while any k-1 shares leak no information about the key.

Default scheme: n=3, k=2 — three independent parties (e.g., NTSB/JTSB,
IFALPA, judicial authority) where any two can decrypt.

Reference: Shamir A. How to share a secret. Communications of the ACM,
22(11), 1979.
"""

import os


# 257-bit prime modulus (NIST SP 800-57 compatible field).
P = 2**257 - 93


def _polinomla_deger(katsayilar: list, x: int) -> int:
    """Evaluate f(x) = k0 + a1*x + a2*x^2 + ... (mod P)."""
    return sum(c * pow(x, i, P) for i, c in enumerate(katsayilar)) % P


def anahtari_paylaristir(ana_anahtar_int: int, n: int = 3, k: int = 2) -> list:
    """
    Split a master key into n Shamir shares with a k-of-n threshold.

    Parameters
    ----------
    ana_anahtar_int : int
        Master key as a big-endian integer (e.g., int.from_bytes(key,"big")).
    n : int
        Total number of shares (default: 3).
    k : int
        Threshold — minimum number of shares required to reconstruct (default: 2).

    Returns
    -------
    list of (int, int)
        n tuples (x_i, y_i) representing the shares.
    """
    if k < 1 or n < k:
        raise ValueError("Require n >= k >= 1.")
    katsayilar = [ana_anahtar_int] + [
        int.from_bytes(os.urandom(32), "big") % P for _ in range(k - 1)
    ]
    return [(i + 1, _polinomla_deger(katsayilar, i + 1)) for i in range(n)]


def anahtari_birlestir(parcalar: list) -> int:
    """
    Reconstruct the master key from at least k shares via Lagrange interpolation.

    Mathematical basis (Shamir, 1979):
        f(0) = sum_i  y_i * prod_{j != i} ( -x_j / (x_i - x_j) )  (mod p)

    Parameters
    ----------
    parcalar : list of (int, int)
        Shares — at least k tuples (x_i, y_i).

    Returns
    -------
    int — reconstructed master key.
    """
    toplam = 0
    for i, (xi, yi) in enumerate(parcalar):
        pay, payda = 1, 1
        for j, (xj, _) in enumerate(parcalar):
            if i != j:
                pay   = (pay   * (-xj))     % P
                payda = (payda * (xi - xj)) % P
        toplam = (toplam + yi * pay * pow(payda, P - 2, P)) % P
    return toplam
