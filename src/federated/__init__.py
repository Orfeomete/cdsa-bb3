"""
CDSA-BB3 src.federated — Federated Aggregation Scaffold
========================================================

Module 6 of the CDSA-BB3 Scenario C FRL extension. Provides
Federated Averaging (FedAvg, McMahan et al. 2017) and FedProx
(Li et al. 2020, μ=0.01) aggregation for the multi-airline pilot
consortium.

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 1.
"""

from .fedavg import FedAvgAggregator  # noqa: F401
from .fedprox import FedProxAggregator  # noqa: F401

__all__ = ["FedAvgAggregator", "FedProxAggregator"]
