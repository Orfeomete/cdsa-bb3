"""Faz A / A6 run configuration — CDSA-BB3 pillar."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.rl_environment.pilot_state_env import PilotStateEnv, ACTIONS

PILLAR = "CDSA-BB3"
N_ACTIONS = 4
STATE_DIM = 10
NEW_STEP_API = True
INFO_TRUE_KEY = "appropriate_action"
ACTION_LABELS = list(ACTIONS)
MODALITY_GROUPS = {"ppg": np.r_[0:3], "ecg": np.r_[3:6], "eeg": np.r_[6:10]}


class _BiasedPilotEnv(PilotStateEnv):
    """Non-IID istemci: durum dagilimina us (power) carpikligi uygular.

    exponent < 1 -> yuksek degerlere yigilma (yorgun filo),
    exponent > 1 -> dusuk degerlere yigilma (dinlenmis filo).
    """

    def __init__(self, exponent: float = 1.0, **kw):
        super().__init__(**kw)
        self.exponent = float(exponent)

    def _sample_state(self):
        return super()._sample_state() ** self.exponent


_CLIENT_EXPONENTS = (0.6, 1.0, 1.6)   # THY, Pegasus, SunExpress (sim)


def make_env(seed: int):
    return PilotStateEnv(seed=seed, max_steps=10_000)


def make_client_envs(seed: int):
    return [_BiasedPilotEnv(exponent=e, seed=seed + i, max_steps=10_000)
            for i, e in enumerate(_CLIENT_EXPONENTS)]

CRITICAL_ACTIONS = set((3,))
