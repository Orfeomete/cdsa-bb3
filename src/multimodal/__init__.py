"""
CDSA-BB3 src.multimodal — Multi-modal Bi-LSTM + Cross-modal Attention
=======================================================================

Module 7 of the CDSA-BB3 Scenario C FRL extension. Provides three
parallel Bidirectional LSTM encoders (PPG, ECG, EEG) and a
cross-modal attention + gating fusion layer that produces the
64-dimensional fused representation consumed by `src.rl_agents`.

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 1.
"""

from .encoders import PPGEncoder, ECGEncoder, EEGEncoder  # noqa: F401
from .fusion import CrossModalAttentionFusion  # noqa: F401

__all__ = [
    "PPGEncoder", "ECGEncoder", "EEGEncoder", "CrossModalAttentionFusion",
]
