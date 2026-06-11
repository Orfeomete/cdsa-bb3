"""
Modality-specific Bidirectional LSTM encoders for CDSA-BB3 — NumPy
reference implementation (v2).

Per-modality configuration:
  PPGEncoder: Bi-LSTM, 32 units, 100 Hz sampling (pulse, SpO2, HRV)
  ECGEncoder: Bi-LSTM, 64 units, 250 Hz sampling (QRS morphology, RR)
  EEGEncoder: Bi-LSTM, 128 units, 256 Hz sampling (alpha/beta/theta/gamma)

Each encoder projects the concatenated forward+backward final hidden
states to a ``latent_dim`` (default 64) representation: h_p (PPG),
h_e (ECG), h_g (EEG).

Scope note (Faz A): compact CPU-scale NumPy forward implementations with
seeded weights and get/set parameter trees for federated exchange.
Framework-scale training is planned under TUBITAK 1001 ARDEB Projects 1+2.
"""

from __future__ import annotations

import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))


class _LSTMCore:
    """Minimal NumPy LSTM (single layer) returning the last hidden state."""

    def __init__(self, input_dim: int, hidden_dim: int, rng: np.random.Generator):
        s = 1.0 / np.sqrt(max(input_dim + hidden_dim, 1))
        self.W = rng.normal(0, s, (4 * hidden_dim, input_dim + hidden_dim))
        self.b = np.zeros(4 * hidden_dim)
        self.hidden_dim = hidden_dim

    def forward(self, x: np.ndarray) -> np.ndarray:
        H = self.hidden_dim
        h = np.zeros(H)
        c = np.zeros(H)
        for t in range(x.shape[0]):
            z = self.W @ np.concatenate([x[t], h]) + self.b
            i, f, g, o = z[:H], z[H:2 * H], z[2 * H:3 * H], z[3 * H:]
            c = _sigmoid(f) * c + _sigmoid(i) * np.tanh(g)
            h = _sigmoid(o) * np.tanh(c)
        return h

    def params(self) -> dict:
        return {"W": self.W, "b": self.b}

    def set_params(self, p: dict) -> None:
        self.W = np.asarray(p["W"], dtype=float)
        self.b = np.asarray(p["b"], dtype=float)


class _BiLSTMEncoder:
    """Bidirectional LSTM over a biometric waveform window.

    Input  x: (T, n_channels)
    Output h: (latent_dim,)  — projection of [h_fwd; h_bwd]
    """

    def __init__(self, n_channels: int, hidden: int, latent_dim: int = 64,
                 seed: int = 42):
        self.latent_dim = latent_dim
        rng = np.random.default_rng(seed)
        self.fwd = _LSTMCore(n_channels, hidden, rng)
        self.bwd = _LSTMCore(n_channels, hidden, rng)
        s = 1.0 / np.sqrt(2 * hidden)
        self.P = rng.normal(0, s, (latent_dim, 2 * hidden))
        self.pb = np.zeros(latent_dim)
        self.n_channels = n_channels

    def forward(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.ndim != 2:
            raise ValueError("encoder expects (T, n_channels)")
        h_fwd = self.fwd.forward(x)
        h_bwd = self.bwd.forward(x[::-1])
        return self.P @ np.concatenate([h_fwd, h_bwd]) + self.pb

    def params(self) -> dict:
        return {"fwd": self.fwd.params(), "bwd": self.bwd.params(),
                "P": self.P, "pb": self.pb}

    def set_params(self, p: dict) -> None:
        self.fwd.set_params(p["fwd"])
        self.bwd.set_params(p["bwd"])
        self.P = np.asarray(p["P"], dtype=float)
        self.pb = np.asarray(p["pb"], dtype=float)


class PPGEncoder(_BiLSTMEncoder):
    def __init__(self, n_channels: int = 3, latent_dim: int = 64, seed: int = 42):
        super().__init__(n_channels, hidden=32, latent_dim=latent_dim, seed=seed)


class ECGEncoder(_BiLSTMEncoder):
    def __init__(self, n_channels: int = 2, latent_dim: int = 64, seed: int = 42):
        super().__init__(n_channels, hidden=64, latent_dim=latent_dim, seed=seed)


class EEGEncoder(_BiLSTMEncoder):
    def __init__(self, n_channels: int = 4, latent_dim: int = 64, seed: int = 42):
        super().__init__(n_channels, hidden=128, latent_dim=latent_dim, seed=seed)
