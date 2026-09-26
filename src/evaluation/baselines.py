"""
Baseline Evaluator Module.
Evaluates the 3 benchmark baseline detectors against temporal test datasets.
"""

from typing import List, Dict, Any
from src.behavioral.baseline import StaticRuleDetector, SemanticOnlyDetector
from src.behavioral.anomaly_detector import BehavioralAnomalyDetector
from src.evaluation.metrics import compute_classification_metrics


class BaselineEvaluator:
    """Evaluates Baseline 1 (Rules), Baseline 2 (Behavioral ML), and Baseline 3 (Semantic Transformer)."""

    def __init__(self):
        self.rule_detector = StaticRuleDetector()
        self.semantic_detector = SemanticOnlyDetector(drift_threshold=0.20)
        self.behavioral_detector = BehavioralAnomalyDetector()

    def evaluate(self, train_events: List[Dict[str, Any]], test_events: List[Dict[str, Any]], baseline_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Runs baseline models on temporal train/test split."""

        # Train behavioral detector on benign events in train_events
        benign_train = [e for e in train_events if e["label"] == "BENIGN"]
        if benign_train:
            self.behavioral_detector.fit(benign_train, baseline_map)

        y_true = [1 if e["label"] == "RUG_PULL" else 0 for e in test_events]

        # 1. Baseline 1: Static Rules
        b1_pred = []
        for e in test_events:
            tool_id = e["tool_id"]
            base = baseline_map.get(tool_id, e)
            res = self.rule_detector.predict(base, e)
            b1_pred.append(1 if res["classification"] == "RUG_PULL" else 0)

        # 2. Baseline 2: Behavioral ML Only (Isolation Forest)
        b2_pred = []
        for e in test_events:
            tool_id = e["tool_id"]
            base = baseline_map.get(tool_id, e)
            score = self.behavioral_detector.predict_anomaly_score(e, base)
            b2_pred.append(1 if score >= 0.40 else 0)

        # 3. Baseline 3: Semantic Detector Only (Transformer Drift)
        b3_pred = []
        for e in test_events:
            tool_id = e["tool_id"]
            base = baseline_map.get(tool_id, e)
            res = self.semantic_detector.predict(base, e)
            b3_pred.append(1 if res["classification"] == "RUG_PULL" else 0)

        return {
            "baseline_1_rules": compute_classification_metrics(y_true, b1_pred),
            "baseline_2_behavioral_ml": compute_classification_metrics(y_true, b2_pred),
            "baseline_3_semantic_transformer": compute_classification_metrics(y_true, b3_pred)
        }
