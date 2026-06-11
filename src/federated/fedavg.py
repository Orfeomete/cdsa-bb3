"""
FedAvg aggregator for CDSA-BB3 — NumPy reference implementation (v2).

Reference: McMahan, B. et al. (2017). AISTATS.

Data-weighted Federated Averaging over parameter dicts for the
multi-airline pilot consortium, with an optional Laplace differential-
privacy hook applied to client updates before aggregation.

Scope note (Faz A): compact CPU-scale reference implementation.
Framework-scale training is planned under TUBITAK 1001 ARDEB Projects 1+2.
"""

from __future__ import annotations

import numpy as np


class FedAvgAggregator:
    """Data-weighted Federated Averaging over nested parameter dicts."""

    def __init__(self, dp_epsilon: float | None = None, dp_sensitivity: float = 1.0,
                 seed: int | None = None):
        self.dp_epsilon = dp_epsilon
        self.dp_sensitivity = dp_sensitivity
        self.rng = np.random.default_rng(seed)
        self.round = 0

    def _laplace(self, arr: np.ndarray) -> np.ndarray:
        scale = self.dp_sensitivity / float(self.dp_epsilon)
        return arr + self.rng.laplace(0.0, scale, size=arr.shape)

    def privatize(self, params: dict) -> dict:
        """Apply Laplace noise (if dp_epsilon is set) to a client update."""
        if self.dp_epsilon is None:
            return params
        return _tree_map(self._laplace, params)

    def aggregate(self, client_params: list[dict],
                  client_weights: list[float] | None = None) -> dict:
        """Weighted average of client parameter trees (weights proportional to data size)."""
        if not client_params:
            raise ValueError("client_params must be non-empty")
        if client_weights is None:
            client_weights = [1.0] * len(client_params)
        w = np.asarray(client_weights, dtype=float)
        if w.sum() <= 0:
            raise ValueError("client_weights must sum to a positive value")
        w = w / w.sum()
        noisy = [self.privatize(p) for p in client_params]
        out = _tree_zeros_like(noisy[0])
        for wi, pi in zip(w, noisy):
            out = _tree_add(out, _tree_scale(pi, float(wi)))
        self.round += 1
        return out


def _tree_map(fn, tree):
    if isinstance(tree, dict):
        return {k: _tree_map(fn, v) for k, v in tree.items()}
    return fn(np.asarray(tree, dtype=float))


def _tree_zeros_like(tree):
    return _tree_map(np.zeros_like, tree)


def _tree_scale(tree, s: float):
    return _tree_map(lambda a: a * s, tree)


def _tree_add(t1, t2):
    if isinstance(t1, dict):
        return {k: _tree_add(t1[k], t2[k]) for k in t1}
    return np.asarray(t1) + np.asarray(t2)


def _tree_sub(t1, t2):
    if isinstance(t1, dict):
        return {k: _tree_sub(t1[k], t2[k]) for k in t1}
    return np.asarray(t1) - np.asarray(t2)


def _tree_sqnorm(tree) -> float:
    if isinstance(tree, dict):
        return float(sum(_tree_sqnorm(v) for v in tree.values()))
    a = np.asarray(tree, dtype=float)
    return float((a * a).sum())
