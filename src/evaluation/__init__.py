"""
Evaluation Framework Package.
Contains metrics computation, baseline evaluation, ablation studies, and experiment execution.
"""

from src.evaluation.metrics import compute_classification_metrics, compute_agent_rag_metrics
from src.evaluation.baselines import BaselineEvaluator
from src.evaluation.ablation import AblationStudyEvaluator
from src.evaluation.experiments import ExperimentRunner

__all__ = [
    "compute_classification_metrics",
    "compute_agent_rag_metrics",
    "BaselineEvaluator",
    "AblationStudyEvaluator",
    "ExperimentRunner"
]
