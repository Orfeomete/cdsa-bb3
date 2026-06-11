# CDSA Scenario C — Paradigm Context for BB3

**Document status:** Reference document supporting the BB3 v2 update.
**Source decision:** CDSA Methodological Unification Decision (Scenario C, frozen status), 21 May 2026.
**Audience:** Repository users (developers, reviewers, replicators) who need to understand the paradigm positioning of CDSA-BB3.

## 1. Why Scenario C exists

A senior aviation professional reviewing the CDSA-APP framework in
May 2026 noted that the three pillars (BB3, MRO, ATM) were using
heterogeneous methodologies — supervised LSTM for BB3, supervised
multi-modal for MRO, reinforcement learning for ATM — which made it
difficult to claim a single paradigm-defining framework. This feedback
was accepted as academically valid, and on 21 May 2026 the author
issued the Scenario C decision: **all three CDSA pillars are unified
under a Federated Reinforcement Learning (FRL) paradigm with
pillar-specific policy network architectures.**

## 2. Three-pillar symmetry under FRL

| Dimension | CDSA-BB3 (this repo) | CDSA-MRO | CDSA-ATM |
|---|---|---|---|
| Domain | Pilot biometrics | Maintenance safety | Air traffic management |
| Policy network | Bi-LSTM (multi-modal) | 1D-CNN + Transformer + LSTM | Multi-Agent PPO (multi-modal) |
| Modalities | PPG + ECG + EEG | Engine + Cyber + Maintenance | Trajectory + ATS + ANSP |
| Federated layer | Pilot consortium | MRO consortium | ANSP consortium |
| XAI | SHAP + counterfactual + LIME | (same) | (same) |
| Privacy | DP (ε ≤ 1.0) + Shamir (2,3) | (same) | (same) |

The paradigm layer (FRL + FedAvg/FedProx), privacy layer (DP + Shamir)
and explainability layer (SHAP + counterfactual + LIME) are **constant
across all three pillars**. What varies is the policy network
architecture, the data modalities, and the federated consortium
structure — each adapted to its specific domain.

## 3. What v2 changes in this repo

The v2 update is **additive only**. The v1.0.0 release tag remains
valid and reproducible:
- Synthetic data generator (n=1179, seed=42) — unchanged
- k-Anonymity + Laplace DP anonymization — unchanged
- AES-256-GCM + Shamir 2/3 cryptography — unchanged
- arXiv preprint v1.0.0 — unchanged

The v2 additions are:
- Five scaffolded `src/` modules for the FRL extension
  (rl_agents, rl_environment, federated, multimodal, xai)
- This paradigm-context document
- A repository-level `figures/` directory with placeholder README
- Updated README.md, CHANGELOG.md, CITATION.cff, .zenodo.json

The scaffolded modules raise `NotImplementedError` when instantiated;
their implementations are deferred to **TÜBİTAK 1001 ARDEB Projects
1 + 2** (September 2026 application cycle; 2027-2030 execution).

## 4. How to read this repo at v1.0.0 vs v2

If you are reading this repo to **reproduce the arXiv preprint v1.0.0**
(cryptographic biometric framework): use the v1.0.0 release tag and
the existing modules (`synthetic_data`, `anonymization`, `cryptography`).
The scaffolded v2 modules can be ignored.

If you are reading this repo to **understand the paradigm context for
the JATM v8 manuscript or the Safety Science Q1 paradigm-defining
article**: use the v2 update notes in README.md and this paradigm
context document. The scaffolded v2 modules document the architectural
commitments.

## 5. Sibling repositories

| Repository | Pillar | Status |
|---|---|---|
| `Orfeomete/cdsa-bb3` (this) | Pilot biometrics | v1.0.0 + v2 scaffold |
| `Orfeomete/cdsa-mro` | Maintenance safety | v1.0.0 |
| `Orfeomete/cdsa-atm` | Air traffic management | v1.0.0 |
| `Orfeomete/cdsa-site` | Public hub at cdsa.app | active |

## 6. Decision document

The CDSA Methodological Unification Decision (Scenario C) is an
internal frozen-status decision document of Istanbul Beykent
University, dated 21 May 2026. Citations to this document use the
following BibTeX entry:

```bibtex
@misc{cantekin2026cdsa_scenario_c,
  author = {Cantekin, Mete},
  title  = {CDSA Methodological Unification Decision (Scenario C, frozen status)},
  year   = 2026,
  month  = may,
  note   = {Internal frozen decision document, Istanbul Beykent University},
  url    = {https://github.com/Orfeomete/cdsa-bb3/blob/main/docs/scenario_c_paradigm_context.md}
}
```

---

**Last updated:** 22 May 2026
**Maintainer:** Mete Cantekin (`metecantekin@gmail.com`, ORCID 0009-0001-6990-6340)
