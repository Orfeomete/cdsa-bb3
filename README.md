# CDSA-BB3 — Complementary Diagnostic Safety Approach

**Synthetic biometric data + anonymization + cryptographic multi-signature for aviation black-box research.**

[![DOI](https://img.shields.io/badge/DOI-pending-yellow.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/arXiv-preprint-b31b1b.svg)](docs/arXiv_preprint.pdf)

---

## Overview

CDSA-BB3 is the open-source reference implementation that accompanies
the doctoral research on the **Complementary Diagnostic Safety Approach
(CDSA)** — a third-generation aviation safety paradigm that augments
traditional Flight Data Recorders (FDR/CVR) with wearable biometric
evidence (HRV, SpO2, GSR) captured under operational conditions.

The framework addresses two structural problems that block biometric
data use in aviation safety investigation:

1. **Real biometric data are inaccessible** — pilots' physiological
   recordings carry trade-secret status under operator agreements and
   special-category protection under GDPR Article 9 and KVKK Article 6.
   We resolve this by generating **deterministic synthetic data** from
   a route × shift calibration matrix grounded in the thesis Annex B.
2. **Single-party access is incompatible with chain-of-custody** —
   raw biometric records cannot sit on a single investigator's disk
   without breaching impartiality. We resolve this by combining
   **AES-256-GCM encryption** with a **Shamir 2/3 secret sharing
   threshold** distributed across NTSB/JTSB, IFALPA, and the
   judicial authority.

This repository contains the **three Python modules** that implement
the prototype (thesis Annex C, 336 lines), the **1179-record reference
dataset** (byte-reproducible with `seed=42`), and the **arXiv preprint
LaTeX submission package** (21 pages, Beykent University imprint).

---

## Paradigm Context — CDSA Scenario C (v2 update, 22 May 2026)

Following the **CDSA Methodological Unification Decision (Scenario C,
frozen status, 21 May 2026)**, this BB3 module is positioned as the
**pilot-biometrics pillar** of a three-pillar **Federated Reinforcement
Learning (FRL)** research programme:

| Pillar | Domain | Companion repo | Companion journal article |
|---|---|---|---|
| **CDSA-BB3** (this) | Pilot biometrics | `Orfeomete/cdsa-bb3` | JATM v8 (Q2, in submission) |
| **CDSA-MRO** | Maintenance safety | `Orfeomete/cdsa-mro` | RESS v2 (Q1, in preparation) |
| **CDSA-ATM** | Air traffic management | `Orfeomete/cdsa-atm` | CEAS v2 (Q2, in preparation) |

A paradigm-defining umbrella article (Safety Science Q1, September 2026
submission target) positions the three pillars under a common
diagnostic-safety paradigm with convergent validation evidence across
the three aviation domains.

The current `src/` layout retains the cryptographic-biometric core
(synthetic data, anonymization, AES-GCM + Shamir SSS) and adds five
**scaffolded FRL modules** for the paradigm extension:

```
src/
├── synthetic_data/      Module 1 — generator (v1.0.0)
├── anonymization/       Module 2 — k-Anonymity + Laplace DP (v1.0.0)
├── cryptography/        Module 3 — AES-GCM + Shamir SSS (v1.0.0)
├── rl_agents/           Module 4 — PPO Actor-Critic (v2 scaffolded)
├── rl_environment/      Module 5 — state-action-reward (v2 scaffolded)
├── federated/           Module 6 — FedAvg + FedProx (v2 scaffolded)
├── multimodal/          Module 7 — Bi-LSTM PPG+ECG+EEG fusion (v2 scaffolded)
└── xai/                 Module 8 — SHAP + counterfactual reasoning (v2 scaffolded)
```

The v2 modules are **scaffolds**: `__init__.py` + placeholder docstrings
documenting the planned interface. Full implementations are deferred to
**TÜBİTAK 1001 ARDEB Projects 1 + 2** (September 2026 application
cycle; 2027-2030 execution). Treat v2 modules as **architectural
commitments**, not as runnable code at v1.0.0.

For the paradigm-defining argument, refer to:
- `docs/scenario_c_paradigm_context.md` (paradigm context summary)
- The CDSA Methodological Unification Decision document (internal,
  cited as `[Cantekin 2026, CDSA Scenario C]`)
- The Safety Science Q1 umbrella article (in preparation, September 2026)

---

---

## Repository Layout

```
cdsa-bb3/
├── src/
│   ├── synthetic_data/      Module 1 — Generator + statistical validation
│   ├── anonymization/       Module 2 — k-Anonymity (k=5) + Laplace DP (eps=1.0)
│   └── cryptography/        Module 3 — AES-256-GCM + Shamir 2/3 threshold
├── data/
│   ├── synthetic_n1179.json              Raw synthetic dataset (n=1179)
│   ├── synthetic_n1179_anon.json         After k-anon + DP
│   └── statistical_validation_report.json
├── paper/
│   ├── main.tex             arXiv submission source (Beykent imprint)
│   ├── references.bib
│   └── images/              5 figures
├── docs/
│   ├── arXiv_preprint.pdf   21-page rendered preprint
│   └── ...
├── examples/
│   ├── quick_start.py       60-second end-to-end demo
│   └── reproduce_thesis.py  Reproduce thesis Section 4.1.6 in one run
├── tests/
│   └── test_prototype.py    pytest suite (5 tests)
├── README.md                this file
├── LICENSE                  MIT (code)
├── LICENSE-DATA             CC BY 4.0 (synthetic dataset)
├── CITATION.cff             machine-readable citation metadata
├── CHANGELOG.md
├── CONTRIBUTING.md
├── requirements.txt         numpy, scipy, cryptography
└── .zenodo.json             Zenodo deposit metadata
```

---

## Quick Start

```bash
git clone https://github.com/Orfeomete/cdsa-bb3.git
cd cdsa-bb3
pip install -r requirements.txt
python examples/quick_start.py
```

Expected output (verbatim, deterministic):

```
Records generated:    1179
Spearman rho(HRV,GSR) = -0.6482  (p < 0.001)
Night SRS mean        = 0.2102
Day   SRS mean        = 0.0704   (Mann-Whitney U, p < 0.001)
k-Anonymity (k=5)     : 1179 records retained
AES-256-GCM + Shamir  : key round-trip OK
```

---

## Module Reference

### Module 1 — Synthetic Data Generation

`src/synthetic_data/generator.py`

Generates n=1179 biometric records over **8 long-haul routes from
Istanbul** (IST-SYD, GRU, NRT, ORD, SIN, JFK, LHR, DXB) and **2 shift
types** (Night, Day). Each record carries HRV (ms), SpO2 (%), GSR (uS),
and the derived Stress-Recovery Score (SRS).

Physiological model (Annex B Table 3):
- HRV  ~ N(65 - SRS * 95,  sigma=5.0), clipped to [18,   78]   ms
- SpO2 ~ N(98.2 - SRS * 4.5, sigma=0.4), clipped to [91,   99.5] %
- GSR  ~ N(5 + SRS * 22,  sigma=1.8),  clipped to [3.2,  24.8] uS

Statistical validation: Shapiro-Wilk per subgroup, Spearman correlation,
Mann-Whitney U one-sided.

### Module 2 — Anonymization

`src/anonymization/anonymizer.py`

- **k-Anonymity (k=5):** records whose (route, shift) combination has
  fewer than 5 members are dropped.
- **Laplace differential privacy (epsilon=1.0):** Laplace noise added
  to HRV (Delta=5.0), SpO2 (Delta=1.0), GSR (Delta=2.0), SRS (Delta=0.05).

Reference: Dwork & Roth, *The Algorithmic Foundations of Differential
Privacy*, 2014.

### Module 3 — Cryptographic Multi-Signature

`src/cryptography/aes_gcm.py` + `src/cryptography/shamir.py`

- **AES-256-GCM** with 96-bit nonce and AAD = `flight_id|timestamp|KARAKUTU-v1`
  binding ciphertext to operational context.
- **Shamir 2/3 secret sharing** over GF(p) with p = 2^257 - 93
  (NIST SP 800-57 compatible 257-bit prime).

Default threshold scheme assigns shares to NTSB/JTSB, IFALPA, and the
judicial authority — any two of three may reconstruct.

References: NIST SP 800-38D (AES-GCM); Shamir, *How to share a secret*,
Communications of the ACM 22(11), 1979.

---

## How to Cite

If you use CDSA-BB3 in academic work, please cite both the software
and the arXiv preprint.

**Software (BibTeX):**

```bibtex
@software{cantekin2026cdsablackbox,
  author    = {Cantekin, Mete},
  title     = {CDSA-BB3: Synthetic Biometric Data, Anonymization
               and Cryptographic Multi-Signature for Aviation Safety
               Investigation},
  year      = 2026,
  month     = may,
  version   = {1.0.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.XXXXXXX},
  url       = {https://github.com/Orfeomete/cdsa-bb3}
}
```

**Preprint (BibTeX):**

```bibtex
@misc{cantekin2026cdsapreprint,
  author       = {Cantekin, Mete},
  title        = {Complementary Diagnostic Safety Approach: Wearable
                  Technologies, Synthetic Data and Cryptographic
                  Multi-Signature for Aviation Black-Box Evolution},
  year         = 2026,
  eprint       = {arXiv:XXXX.XXXXX},
  primaryClass = {cs.CR}
}
```

`CITATION.cff` provides the same metadata in a machine-readable form
recognized by Zenodo, GitHub, and academic indexers.

---

## License

- **Code** is released under the **MIT License** (`LICENSE`).
- **Synthetic dataset** is released under **Creative Commons Attribution
  4.0 International** (`LICENSE-DATA`).

Synthetic data contain **no real persons, flights, operators, or
incidents**. They are produced from a documented generative model
with a fixed random seed and are intended for methodological
reproduction.

---

## Provenance and Related Work

This repository is part of the **CDSA framework ecosystem** maintained
under [`Orfeomete`](https://github.com/Orfeomete):

| Repository | Role |
|---|---|
| [`cdsa-site`](https://github.com/Orfeomete/cdsa-site) | Public hub & landing page (cdsa.app) |
| [`cdsa-bb3`](https://github.com/Orfeomete/cdsa-bb3) | **This repo** — investigation-side academic prototype |
| [`cdsa-mro`](https://github.com/Orfeomete/cdsa-mro) | Maintenance-organisation module (SDG + RL) |
| [`hipoksi-app-`](https://github.com/Orfeomete/hipoksi-app-) | PilotO2 hypoxia simulator |
| [`pilotguard-app-`](https://github.com/Orfeomete/pilotguard-app-) | Pre-flight readiness monitor |
| [`PilotReflect-new`](https://github.com/Orfeomete/PilotReflect-new) | Post-flight EFB debrief |
| [`pilotsense-auth`](https://github.com/Orfeomete/pilotsense-auth) | Cryptographic 2/3 signature demo |
| [`pilotsense-ops`](https://github.com/Orfeomete/pilotsense-ops) | Anonymized fleet monitoring |

---

## v2 Update Notes (22 May 2026)

The repository structure was updated on 22 May 2026 following the CDSA
Scenario C paradigm decision. The update is **additive** — all v1.0.0
content (synthetic data, anonymization, cryptography modules; reference
dataset; arXiv preprint package) remains unchanged and accessible.
Five new src/ modules (rl_agents, rl_environment, federated, multimodal,
xai) have been scaffolded for the FRL paradigm extension. A new
`figures/` directory has been added for repository-level figures
(parallel to the existing `paper/images/`). The CHANGELOG, CITATION.cff
and `.zenodo.json` have been updated to reflect the paradigm context.

The v1.0.0 release tag remains valid and reproducible; v2.0.0 release
is planned for Q4 2026 following TÜBİTAK Project 1+2 acceptance.

---

## Acknowledgements

This software supports the doctoral thesis in preparation at **Istanbul
Beykent University, Department of Computer Engineering**, under the
supervision of Assoc. Prof. Dr. Ibrahim Furkan INCE.

Per the **Authorship and Citation Rule** (frozen decision, 15 May 2026),
the supervisor appears only on the thesis manuscript itself; in this
software and in all derived articles and preprints, sole authorship is
attributed to Mete Cantekin.

---

## Contact

Mete Cantekin — `metecantekin@gmail.com`
ORCID: [0009-0001-6990-6340](https://orcid.org/0009-0001-6990-6340)
