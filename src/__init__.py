"""
CDSA-BB3 Python package
========================

v1.0.0 modules (cryptographic-biometric core):
  - synthetic_data    : Deterministic generator + statistical validation
  - anonymization     : k-Anonymity + Laplace differential privacy
  - cryptography      : AES-256-GCM + Shamir 2/3 secret sharing

v2 scaffolded modules (Scenario C FRL extension):
  - rl_agents         : PPO Actor-Critic
  - rl_environment    : Gymnasium-compatible Markov decision process
  - federated         : FedAvg + FedProx aggregation
  - multimodal        : PPG + ECG + EEG Bi-LSTM + cross-modal attention
  - xai               : SHAP + counterfactual + LIME

Full implementations of v2 modules are planned under TÜBİTAK 1001
ARDEB Projects 1 + 2 (September 2026 application cycle).

References:
  - Cantekin, M. (2026). CDSA Methodological Unification Decision
    (Scenario C, frozen status). Istanbul Beykent University.
"""

__version__ = "1.0.0"
__paradigm__ = "Scenario C — Federated Reinforcement Learning"
