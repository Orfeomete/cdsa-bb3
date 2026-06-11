"""Unit tests for the CDSA-BB3 v2 modules (Faz A implementation)."""

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.federated.fedavg import FedAvgAggregator
from src.federated.fedprox import FedProxAggregator
from src.multimodal.encoders import PPGEncoder, ECGEncoder, EEGEncoder
from src.multimodal.fusion import CrossModalAttentionFusion
from src.rl_agents.ppo_actor_critic import PPOActorCritic
from src.rl_environment.pilot_state_env import PilotStateEnv
from src.xai.counterfactual import CounterfactualExplainer
from src.xai.lime_explainer import LIMEExplainer
from src.xai.shap_explainer import SHAPModalityExplainer

RNG = np.random.default_rng(0)
L = 64


def _toy(scale):
    return {"W": np.full((2, 2), float(scale))}


def test_fedavg_and_fedprox():
    out = FedAvgAggregator().aggregate([_toy(0), _toy(1)], [1, 3])
    assert np.allclose(out["W"], 0.75)
    prox = FedProxAggregator(mu=0.5)
    assert np.isclose(prox.proximal_penalty(_toy(2), _toy(0)), 0.5 * 0.5 * 16)


def test_bilstm_encoders_and_fusion():
    h_p = PPGEncoder(seed=1).forward(RNG.normal(size=(30, 3)))
    h_e = ECGEncoder(seed=1).forward(RNG.normal(size=(40, 2)))
    h_g = EEGEncoder(seed=1).forward(RNG.normal(size=(50, 4)))
    for h in (h_p, h_e, h_g):
        assert h.shape == (L,) and np.all(np.isfinite(h))
    # bidirectionality: reversing input changes the embedding
    enc = PPGEncoder(seed=1)
    x = RNG.normal(size=(20, 3))
    assert not np.allclose(enc.forward(x), enc.forward(x[::-1]))
    out, gates = CrossModalAttentionFusion(seed=2).forward(h_p, h_e, h_g, return_gates=True)
    assert out.shape == (L,) and set(gates) == {"ppg", "ecg", "eeg"}


def test_encoder_param_roundtrip():
    enc = EEGEncoder(seed=3)
    x = RNG.normal(size=(15, 4))
    h = enc.forward(x)
    other = EEGEncoder(seed=99)
    other.set_params(enc.params())
    assert np.allclose(h, other.forward(x))


def test_env_reward_rules():
    env = PilotStateEnv(seed=5, max_steps=4)
    s, _ = env.reset()
    assert s.shape == (10,)
    env._state = np.array([.5, .2, .5, .9, .8, .8, .2, .2, .2, .2])  # ecg arr + low spo2 -> critical(3)
    _, r, _, _, info = env.step(3)
    assert r == 10.0 and info["appropriate_action"] == 3
    env._state = np.array([.5, .2, .5, .9, .8, .8, .2, .2, .2, .2])
    _, r2, _, _, _ = env.step(0)  # missed critical
    assert r2 == -25.0


def test_ppo_learns_on_pilot_env():
    env = PilotStateEnv(seed=11, max_steps=64)
    agent = PPOActorCritic(fused_dim=10, n_actions=4, hidden=32, lr=0.05, seed=11)

    def rollout(rand=False):
        s, _ = env.reset(seed=123)
        S, A, LP, Rw, V, D = [], [], [], [], [], []
        for _ in range(64):
            if rand:
                a, logp, v = int(RNG.integers(4)), np.log(0.25), 0.0
            else:
                a, logp, v = agent.act(s)
            s2, r, term, trunc, _ = env.step(a)
            S.append(s); A.append(a); LP.append(logp); Rw.append(r); V.append(v); D.append(term or trunc)
            s = s2
        return S, A, LP, Rw, V, D

    base = np.mean(rollout(rand=True)[3])
    for _ in range(30):
        S, A, LP, Rw, V, D = rollout()
        adv, ret = agent.compute_gae(Rw, V, D)
        agent.update(S, A, LP, adv, ret, epochs=3)
    trained = np.mean(rollout()[3])
    assert trained > base + 1.0, f"trained={trained:.2f} base={base:.2f}"


def test_xai_suite():
    def head(h_p, h_e, h_g):
        f = np.array([h_p.mean(), h_e.mean(), h_g.mean()])
        W = np.array([[1.0, .2, .2], [.1, .2, 1.8], [.2, .3, 1.4], [.2, 1.6, .2]])
        return W @ f  # action1 (fatigue) eeg-driven, action3 ecg-driven
    lat = {"ppg": np.full(L, .2), "ecg": np.full(L, .3), "eeg": np.full(L, 2.0)}
    shap = SHAPModalityExplainer(head)
    assert max(shap.contribution_percentages(lat).items(), key=lambda kv: kv[1])[0] == "eeg"
    cf = CounterfactualExplainer(head, action_labels=["nominal", "fatigue", "reduced_sa", "critical"])
    assert cf.counterfactual(lat, "eeg")["decision_changed"] is True
    lime = LIMEExplainer(lambda x: np.array([2.5 * x[0], 0.0]), n_samples=300, seed=4)
    assert lime.explain(np.ones(3), action=0)["top_features"][0]["index"] == 0
