"""
Cross-modal attention + gating fusion for CDSA-BB3 — NumPy reference
implementation (v2).

Reference: Vaswani et al. (2017), Attention Is All You Need, NeurIPS.

Token set: {h_ppg, h_ecg, h_eeg}. Per-modality sigmoid gates, scaled
dot-product attention, gated sum, linear head -> fusion_dim for the PPO
Actor-Critic head. Gating scores feed the XAI layer and the platform
FRL Agent Panel.

Scope note (Faz A): compact CPU-scale forward implementation.
Framework-scale training under TUBITAK 1001 ARDEB Projects 1+2.
"""

from __future__ import annotations

import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))


class CrossModalAttentionFusion:
    """Gated cross-modal attention over the three biometric modality latents."""

    MODALITIES = ("ppg", "ecg", "eeg")

    def __init__(self, latent_dim: int = 64, fusion_dim: int = 64, seed: int = 42):
        self.latent_dim = latent_dim
        self.fusion_dim = fusion_dim
        rng = np.random.default_rng(seed)
        s = 1.0 / np.sqrt(latent_dim)
        self.Wq = rng.normal(0, s, (latent_dim, latent_dim))
        self.Wk = rng.normal(0, s, (latent_dim, latent_dim))
        self.Wv = rng.normal(0, s, (latent_dim, latent_dim))
        self.Wg = rng.normal(0, s, (len(self.MODALITIES), latent_dim))
        self.bg = np.zeros(len(self.MODALITIES))
        self.Wo = rng.normal(0, s, (fusion_dim, latent_dim))
        self.bo = np.zeros(fusion_dim)

    def forward(self, h_ppg, h_ecg, h_eeg, return_gates: bool = False):
        H = np.stack([np.asarray(h, dtype=float) for h in (h_ppg, h_ecg, h_eeg)])
        if H.shape[1] != self.latent_dim:
            raise ValueError(f"expected latent_dim={self.latent_dim}")
        gates = _sigmoid(np.einsum("ml,ml->m", self.Wg, H) + self.bg)
        Q, K, V = H @ self.Wq.T, H @ self.Wk.T, H @ self.Wv.T
        A = Q @ K.T / np.sqrt(self.latent_dim)
        A = np.exp(A - A.max(axis=1, keepdims=True))
        A = A / A.sum(axis=1, keepdims=True)
        H_attn = A @ V
        h_fusion = self.Wo @ (gates[:, None] * H_attn).sum(axis=0) + self.bo
        if return_gates:
            return h_fusion, dict(zip(self.MODALITIES, gates.tolist()))
        return h_fusion

    def params(self) -> dict:
        return {"Wq": self.Wq, "Wk": self.Wk, "Wv": self.Wv,
                "Wg": self.Wg, "bg": self.bg, "Wo": self.Wo, "bo": self.bo}

    def set_params(self, p: dict) -> None:
        for n in ("Wq", "Wk", "Wv", "Wg", "bg", "Wo", "bo"):
            setattr(self, n, np.asarray(p[n], dtype=float))
