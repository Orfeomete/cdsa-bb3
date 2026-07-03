# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

## [2.2.0] — 2026-07-03

### Added (Faz B/C/D revision-preparation experiments; seeded, CPU-scale)
- Faz B: inference-time robustness + confusion-matrix evaluation and a
  tempo-aware-reward retraining experiment — `experiments/faz_b_robustness.py`,
  `experiments/faz_b_dynamic_reward.py` + seeded output JSONs under
  `experiments/results/`.
- Faz C: differential-privacy ε sweep (ε = 0.5 / 2.0) and entropy-targeted
  exploration (coef 0.01 / 0.05), each a separate 160-round FedProx
  retraining — `experiments/faz_c_dp_sweep.py`, `experiments/faz_c_entropy.py`
  + output JSONs.
- Faz D: decoy-signal (group-Shapley) attribution test and
  recall-floor-gated exploration — `experiments/faz_d_decoy.py`,
  `experiments/faz_d_gated_entropy.py` + output JSONs.
- Per-phase result panels with honesty bands at https://cdsa.app/bb3/.

### Findings (honest summary — numbers verbatim from `experiments/results/*.json`)
- Faz B: modality ablation independently confirms the SHAP ranking
  (dropping ECG sends critical recall from 0.917 to 0.041; dropping PPG
  pushes the model into an all-alert mode); the two intermediate alert
  classes (fatigue_alert, reduced_sa_alert) are never predicted
  (recall 0) in these conditions.
- Faz C: the ε sweep and entropy conditions leave class coverage
  unchanged — the two intermediate alert classes remain uncovered in
  all configurations.
- Faz D: the decoy test is passed cleanly (attribution 6.4% vs the 25%
  uniform share); gated exploration (floor 0.90) raises critical recall
  to 0.975 (gate_on ratio 0.5).

### Unchanged
- Published core code, environments and Faz A outputs — no behavioural
  changes.
- The v2.1.0 release and its Zenodo DOI remain valid; this v2.2.0 release
  archives the Faz B/C/D outputs on Zenodo.

## [2.0.0-scaffold] — 2026-05-22

### Added (Scenario C paradigm alignment, additive only)
- README.md: new "Paradigm Context — CDSA Scenario C" section
  positioning CDSA-BB3 as the pilot-biometrics pillar of the
  three-pillar Federated Reinforcement Learning (FRL) research
  programme.
- `src/rl_agents/` (scaffold) — PPO Actor-Critic agent skeleton
  with placeholder `PPOActorCritic` class.
- `src/rl_environment/` (scaffold) — Gymnasium-compatible
  `PilotStateEnv` skeleton mapping PPG + ECG + EEG window to the
  four-class action space.
- `src/federated/` (scaffold) — `FedAvgAggregator` + `FedProxAggregator`
  skeletons for the multi-airline pilot consortium.
- `src/multimodal/` (scaffold) — `PPGEncoder` (32 units, 100 Hz),
  `ECGEncoder` (64 units, 250 Hz), `EEGEncoder` (128 units, 256 Hz)
  Bi-LSTM skeletons and `CrossModalAttentionFusion` (Vaswani et al.
  2017) skeleton.
- `src/xai/` (scaffold) — `SHAPModalityExplainer`,
  `CounterfactualExplainer`, `LIMEExplainer` skeletons aligned with
  EASA AI Roadmap Level 2 AI/ML explainability requirements.
- `figures/` directory with placeholder README and `.gitkeep`.
- `docs/scenario_c_paradigm_context.md` — full paradigm context
  reference document for BB3 v2.
- `CITATION.cff`: added FRL/multi-modal/XAI/CDSA-paradigm keywords,
  Scenario C decision reference, JATM v8 and Safety Science v1
  sibling article references.
- `.zenodo.json`: added FRL/multi-modal/XAI keywords and
  related-identifier entries for the three-pillar sibling repos.

### Not Changed
- v1.0.0 modules (`synthetic_data`, `anonymization`, `cryptography`)
  are byte-identical to the v1.0.0 release. The v1.0.0 release tag
  remains valid and reproducible.
- The 1179-record reference dataset is unchanged.
- The arXiv preprint v1.0.0 package (`paper/main.tex`, references,
  images, rendered PDF) is unchanged.
- Tests (`tests/test_prototype.py`) remain at 5 passing tests.
- Authorship policy (single-author per the CDSA Authorship Rule)
  is unchanged.

### Notes
- The v2 scaffolded modules raise `NotImplementedError` when
  instantiated. Treat them as **architectural commitments**, not
  as runnable code at v2-scaffold stage.
- Full implementations of the scaffolded modules are deferred to
  TÜBİTAK 1001 ARDEB Projects 1 + 2 (Sept 2026 application cycle;
  2027-2030 execution).
- The v2.0.0 final release is planned for Q4 2026 following
  TÜBİTAK project acceptance.

## [1.0.0] — 2026-05-15

### Added
- Module 1 — Synthetic data generator (`src/synthetic_data/generator.py`)
  reproducing thesis Annex B Table 3 calibration matrix; produces
  n=1179 biometric records deterministically with `seed=42`.
- Module 1 — Statistical validation harness (Shapiro-Wilk, Spearman,
  Mann-Whitney U) returning a machine-readable report.
- Module 2 — Two-layer anonymizer (`src/anonymization/anonymizer.py`)
  with k-Anonymity (k=5) and Laplace differential privacy (epsilon=1.0).
- Module 3a — AES-256-GCM authenticated encryption with AAD binding
  flight identifier, timestamp and box identity
  (`src/cryptography/aes_gcm.py`).
- Module 3b — Shamir 2/3 secret sharing over GF(2^257 - 93) with
  Lagrange reconstruction (`src/cryptography/shamir.py`).
- Reference dataset: `data/synthetic_n1179.json` + anonymized variant
  + statistical validation report.
- arXiv preprint submission package: LaTeX source (`paper/main.tex`),
  bibliography (`paper/references.bib`), 5 figures (`paper/images/`),
  rendered 21-page PDF (`docs/arXiv_preprint.pdf`).
- Examples: `examples/quick_start.py`, `examples/reproduce_thesis.py`.
- Tests: `tests/test_prototype.py` (pytest, 5 tests).
- Metadata: README, LICENSE (MIT), LICENSE-DATA (CC-BY 4.0),
  CITATION.cff, .zenodo.json, requirements.txt, .gitignore.

### Notes
- The cryptographic module is a pedagogical implementation of the
  thesis architecture and is **not** intended for production cryptographic
  use. For production deployments, use a vetted threshold-cryptography
  library and an HSM-backed key custody scheme.

## [1.1.0] — Planned (Q3 2026)

### Planned
- HSM integration adapter for AES key custody.
- Additional generative variants (5 short-haul routes, helicopter MRO).
- Replication harness for ICAO Annex 13 chain-of-custody scenarios.
- Notebook walkthrough of the full pipeline (`examples/walkthrough.ipynb`).

## [2.0.0] — Planned (Q4 2026)

### Planned (full v2 release following TÜBİTAK Project 1+2 acceptance)
- `src/rl_agents/`: full PPO Actor-Critic implementation
- `src/rl_environment/`: full Gymnasium-compatible MDP
- `src/federated/`: full FedAvg + FedProx aggregation
- `src/multimodal/`: full PPG + ECG + EEG Bi-LSTM with cross-modal
  attention fusion
- `src/xai/`: full SHAP + counterfactual + LIME pipeline
- Training scripts for multi-airline pilot consortium
- Pilot saha doğrulama verisi (real-pilot validation data, if
  Project 1 ethics approval granted)
- Multi-modal sensor fusion via Graph Neural Network
  (Project TÜBİTAK 1001 #2 outputs)

## [2.1.0] — 2026-06-12 (Faz A implementation)
### Added
- `src/federated/`: FedAvgAggregator + FedProxAggregator NumPy reference
  implementations (multi-airline pilot consortium, Laplace DP hook,
  proximal utilities). Replaces v2.0.0-scaffold stubs.
- `src/multimodal/`: PPGEncoder / ECGEncoder / EEGEncoder (Bidirectional
  LSTM, 32/64/128 units) + CrossModalAttentionFusion (gating + scaled
  dot-product attention), federated param get/set.
- `src/rl_agents/ppo_actor_critic.py`: NumPy PPO Actor-Critic over the
  4-class action space (nominal / fatigue / reduced-SA / critical).
- `src/rl_environment/pilot_state_env.py`: PilotStateEnv — seeded
  synthetic 10-dim / 4-action cognitive-state environment.
- `src/xai/`: SHAPModalityExplainer (exact Shapley), Counterfactual
  Explainer (auditor JSON), LIMEExplainer (ridge surrogate).
- `tests/test_v2_modules.py`: 6 unit tests incl. PPO learning check.
  Total suite: 11/11 green. v1.0.0 modules (anonymization, cryptography,
  synthetic_data) unchanged.
### Notes
- Faz A scope: CPU-scale reference implementations (zero server cost).
  Framework-scale training remains under TUBITAK 1001 Projects 1+2 (Faz B).

### Changed (11 Jun 2026, A6 runs)
- PPOActorCritic: reward_scale + global gradient-norm clipping.
- experiments/: faz_a_staged.py + faz_a_config.py + results/ (seeded,
  checkpointed CPU-scale federated runs; see CDSA_FazA_A6 report).
