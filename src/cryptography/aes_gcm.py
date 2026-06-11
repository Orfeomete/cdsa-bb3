"""
Module 3.1 — AES-256-GCM Record Encryption
============================================

Authenticated encryption with associated data (AEAD) for individual
biometric records. AAD binds flight identifier, timestamp, and box
identity so any tampering with metadata invalidates the GCM tag.

Reference: NIST SP 800-38D (Galois/Counter Mode).
"""

import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def kayit_sifrele(kayit: dict, anahtar: bytes, ucus_id: str, zaman: str) -> dict:
    """
    Encrypt a single biometric record with AES-256-GCM.

    AAD format: "<flight_id>|<timestamp>|KARAKUTU-v1"
    This binds the ciphertext to its operational context so that
    detaching metadata triggers a GCM authentication failure on decrypt.

    Parameters
    ----------
    kayit : dict
        Record payload (JSON-serializable).
    anahtar : bytes
        AES key (32 bytes for AES-256).
    ucus_id : str
        Flight identifier (e.g., "TC-XXX-2026042").
    zaman : str
        ISO-8601 timestamp.

    Returns
    -------
    dict — {nonce, sifreli, aad} all as hex/utf-8 strings.
    """
    aesgcm = AESGCM(anahtar)
    nonce = os.urandom(12)  # 96-bit, per NIST recommendation
    aad = f"{ucus_id}|{zaman}|KARAKUTU-v1".encode()
    veri = json.dumps(kayit).encode()
    sifreli = aesgcm.encrypt(nonce, veri, aad)
    return {
        "nonce":   nonce.hex(),
        "sifreli": sifreli.hex(),
        "aad":     aad.decode(),
    }


def kayit_desifre(sifreli_kayit: dict, anahtar: bytes) -> dict:
    """
    Decrypt a record produced by kayit_sifrele() and verify AAD integrity.

    Raises
    ------
    cryptography.exceptions.InvalidTag
        If the ciphertext or AAD has been tampered with.

    Returns
    -------
    dict — decrypted record payload.
    """
    aesgcm = AESGCM(anahtar)
    nonce = bytes.fromhex(sifreli_kayit["nonce"])
    sifreli = bytes.fromhex(sifreli_kayit["sifreli"])
    aad = sifreli_kayit["aad"].encode()
    acik = aesgcm.decrypt(nonce, sifreli, aad)
    return json.loads(acik)
