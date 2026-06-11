# Cryptography Notes — Module 3 Design

This document records the rationale behind the cryptographic choices in
`src/cryptography/aes_gcm.py` and `src/cryptography/shamir.py`.

## Threat model

We assume an adversary that:

- Has read access to the encrypted record payload (`sifreli` + `nonce`).
- May modify any byte of `sifreli`, `nonce`, or `aad`.
- Holds **at most one** of the three Shamir shares.

We do **not** assume protection against side-channel attacks on the
implementation, nor against an adversary that compromises the host
running the AESGCM operations.

## Why AES-256-GCM

- **AEAD primitive.** Confidentiality and integrity in one pass.
- **AAD binding.** We bind the ciphertext to a flight identifier, a
  timestamp and a fixed string `KARAKUTU-v1`. Detaching metadata or
  replaying ciphertext under a different flight invalidates the
  16-byte tag and forces a clean failure on decrypt.
- **NIST-recommended.** SP 800-38D specifies the construction.

### Nonce discipline

GCM nonces must never repeat under the same key. We use 12 bytes (96 bit)
sampled fresh per record from `os.urandom()` (CSPRNG). At `n = 2^32`
records under one key, the collision probability is approximately
`2^-32` — acceptable for the thesis prototype. Production deployments
should rekey periodically or use a deterministic IV-derivation scheme.

### AAD format

```
<flight_id>|<ISO-8601 timestamp>|KARAKUTU-v1
```

`KARAKUTU-v1` is a version tag so that a future change to the AAD
format does not silently re-decrypt old ciphertexts.

## Why Shamir 2-of-3 (not 3-of-3 or threshold ECDSA)

We want:

1. **Multi-party custody** of the AES master key — no single party can
   unilaterally decrypt the black-box payload.
2. **Robustness** to one party going offline or being legally enjoined.

A 3-of-3 scheme is brittle (any one party can veto decryption); a
threshold ECDSA scheme is overkill (we only need to share the
*decryption key*, not sign on its behalf). Shamir 2-of-3 over a prime
field is the minimum scheme that satisfies (1) and (2) and is
implementable in roughly 40 lines.

## Prime modulus

```
p = 2^257 - 93
```

A 257-bit prime, NIST SP 800-57 (Rev. 5) compatible at the 128-bit
security level for symmetric-key wrapping. The 257-bit width
accommodates a full 256-bit AES key as the constant term of the Shamir
polynomial without truncation.

## Reconstruction (Lagrange)

For shares `(x_i, y_i)`,

```
f(0) = sum_i  y_i * prod_{j != i} ( -x_j / (x_i - x_j) )   (mod p)
```

implemented in `anahtari_birlestir()` using `pow(denominator, p - 2, p)`
for modular inverse via Fermat's little theorem. This requires
`gcd(denominator, p) = 1`, which is guaranteed because `p` is prime and
the denominators are sums of small share indices.

## Pedagogical scope

The module is sized for **doctoral-thesis reproducibility** and **academic
peer review** — not production cryptographic use. Production deployments
should:

- Use an HSM-backed key custody scheme (FIPS 140-3 Level 3+).
- Apply formal threshold-signature libraries such as `frost` or `crysol`.
- Audit nonce generation and AAD construction with KAT vectors.
- Run with a key-rotation policy and a key-history archive.

## References

- National Institute of Standards and Technology. *SP 800-38D —
  Recommendation for Block Cipher Modes of Operation: Galois/Counter
  Mode (GCM) and GMAC*. NIST. 2007.
- National Institute of Standards and Technology. *SP 800-57 Part 1 Rev. 5 —
  Recommendation for Key Management*. NIST. 2020.
- Shamir A. How to share a secret. *Communications of the ACM*,
  22(11):612-613. 1979.
