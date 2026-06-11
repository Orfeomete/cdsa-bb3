"""
SHAP modality contribution explainer for CDSA-BB3 — NumPy reference
implementation (v2).

Reference: Lundberg & Lee (2017), NeurIPS.

Exact Shapley values over the three ATM modalities (trajectory / ATS
events / ANSP coordination) by full 2^3 coalition enumeration. A modality
absent from a coalition is replaced by its baseline latent (default: zeros).
"""

from __future__ import annotations

from itertools import combinations
from math import factorial

import numpy as np

MODALITIES = ("ppg", "ecg", "eeg")


class SHAPModalityExplainer:
    """Exact Shapley values over modality groups.

    predict_fn : callable(h_ppg, h_ecg, h_eeg) -> np.ndarray
    """

    def __init__(self, predict_fn, baselines: dict | None = None):
        self.predict_fn = predict_fn
        self.baselines = baselines or {}

    def _eval(self, latents: dict, coalition: tuple) -> np.ndarray:
        args = []
        for m in MODALITIES:
            if m in coalition:
                args.append(np.asarray(latents[m], dtype=float))
            else:
                base = self.baselines.get(m)
                args.append(np.zeros_like(np.asarray(latents[m], dtype=float))
                            if base is None else np.asarray(base, dtype=float))
        return np.asarray(self.predict_fn(*args), dtype=float)

    def shap_values(self, latents: dict, action: int | None = None) -> dict:
        full = self._eval(latents, MODALITIES)
        a = int(np.argmax(full)) if action is None else int(action)
        n = len(MODALITIES)
        values = {}
        for m in MODALITIES:
            others = [x for x in MODALITIES if x != m]
            phi = 0.0
            for k in range(n):
                for S in combinations(others, k):
                    wgt = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                    phi += wgt * (self._eval(latents, tuple(S) + (m,))[a]
                                  - self._eval(latents, tuple(S))[a])
            values[m] = float(phi)
        return values

    def contribution_percentages(self, latents: dict,
                                 action: int | None = None) -> dict:
        phi = self.shap_values(latents, action=action)
        total = sum(abs(v) for v in phi.values())
        if total == 0:
            return {m: 0.0 for m in MODALITIES}
        return {m: round(100.0 * abs(v) / total, 1) for m, v in phi.items()}
