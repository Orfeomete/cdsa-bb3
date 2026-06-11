"""
PilotStateEnv — NumPy reference implementation (v2).

A Gymnasium-style synthetic pilot cognitive-state environment for the
CDSA-BB3 agent.

State  s (10-dim, normalised [0,1]): PPG-derived HRV/SpO2 (3), ECG
       morphology / arrhythmia (3), EEG band powers
       (alpha/beta/theta/gamma summarised, 4).
Action a (4 discrete): nominal (0), mental fatigue alert (1),
       reduced situational-awareness alert (2), critical capacity
       overflow (3).
Reward: correct +10 · false alert -5 · missed critical -25 ·
        mild mismatch -1.

The hidden "appropriate action" is derived from the state by a rule set
(elevated EEG theta -> fatigue; low EEG/HRV -> reduced SA; ECG
arrhythmia + low SpO2 -> critical), so learning is measurable while the
environment stays fully synthetic and reproducible (seeded).

Scope note (Faz A): CPU-scale synthetic environment. Real-pilot field
validation is planned under TUBITAK 1001 ARDEB Projects 1+2 (Faz B).
"""

from __future__ import annotations

import numpy as np

ACTIONS = ("nominal", "fatigue_alert", "reduced_sa_alert", "critical_overflow")


class PilotStateEnv:
    """Synthetic three-modality pilot cognitive-state environment (seeded)."""

    N_ACTIONS = 4
    STATE_DIM = 10

    def __init__(self, seed: int = 42, max_steps: int = 200):
        self.rng = np.random.default_rng(seed)
        self.max_steps = int(max_steps)
        self._t = 0
        self._state = None

    def _appropriate_action(self, s: np.ndarray) -> int:
        hrv, spo2 = s[0], s[1]
        ecg_arr = s[3:6].max()
        theta = s[8]                 # EEG theta band power
        eeg_low = s[6:10].mean()
        if ecg_arr > 0.75 and spo2 < 0.4:
            return 3                 # critical capacity overflow
        if theta > 0.7:
            return 1                 # mental fatigue
        if eeg_low < 0.3 and hrv < 0.4:
            return 2                 # reduced situational awareness
        return 0

    def _sample_state(self) -> np.ndarray:
        return self.rng.uniform(0, 1, self.STATE_DIM)

    def reset(self, seed: int | None = None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self._t = 0
        self._state = self._sample_state()
        return self._state.copy(), {}

    def step(self, action: int):
        if self._state is None:
            raise RuntimeError("call reset() first")
        a_true = self._appropriate_action(self._state)
        if action == a_true:
            reward = 10.0
        elif a_true == 3 and action < 3:
            reward = -25.0           # missed critical state
        elif action != 0 and a_true == 0:
            reward = -5.0            # false alert
        else:
            reward = -1.0
        self._t += 1
        truncated = self._t >= self.max_steps
        self._state = self._sample_state()
        info = {"appropriate_action": a_true, "appropriate_label": ACTIONS[a_true]}
        return self._state.copy(), reward, False, truncated, info
