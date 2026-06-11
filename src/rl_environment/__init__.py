"""
CDSA-BB3 src.rl_environment — State-Action-Reward Environment Scaffold
========================================================================

Module 5 of the CDSA-BB3 Scenario C FRL extension. Provides a
Gymnasium-compatible environment that wraps the multi-modal biometric
stream (PPG + ECG + EEG) as a Markov decision process for PPO training.

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 1.
"""

from .pilot_state_env import PilotStateEnv  # noqa: F401

__all__ = ["PilotStateEnv"]
