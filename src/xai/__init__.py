"""
CDSA-BB3 src.xai — Explainable AI Layer Scaffold
==================================================

Module 8 of the CDSA-BB3 Scenario C FRL extension. Provides three
explainability techniques aligned with the EASA AI Roadmap Level 2
AI/ML "Concepts of Design" explainability requirement:

  shap.py            — SHAP modality contribution analysis
                        (Lundberg & Lee 2017)
  counterfactual.py  — Counterfactual reasoning
                        (Wachter et al. 2017)
  lime.py            — Local interpretable model-agnostic explanations
                        (Ribeiro et al. 2016)

Outputs are JSON-serialised per the schema in
`docs/xai_output_schema.json` (planned).

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 2 (GNN + certification).
"""

from .shap_explainer import SHAPModalityExplainer  # noqa: F401
from .counterfactual import CounterfactualExplainer  # noqa: F401
from .lime_explainer import LIMEExplainer  # noqa: F401

__all__ = [
    "SHAPModalityExplainer", "CounterfactualExplainer", "LIMEExplainer",
]
