"""
CDSA-BB3 src.rl_agents — PPO Actor-Critic Agent Scaffold
=========================================================

Module 4 of the CDSA-BB3 Scenario C FRL extension. Provides the
Proximal Policy Optimization (PPO) Actor-Critic agent that consumes
the fused multi-modal representation from `src.multimodal` and
produces decisions over the four-class action space:

  a1 — nominal
  a2 — mental fatigue alert
  a3 — reduced situational awareness alert
  a4 — critical capacity overflow intervention

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 1 (Sept 2026 cycle).
"""

from .ppo_actor_critic import PPOActorCritic  # noqa: F401

__all__ = ["PPOActorCritic"]
