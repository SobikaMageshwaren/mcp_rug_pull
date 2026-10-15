"""
Supervised Machine Learning Threat Classifier for MCP Attack Vectors.
Uses Random Forest ensemble to predict exact attack probability distributions
across MITRE ATLAS & CTI threat categories based on multi-modal evidence.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import RandomForestClassifier


CLASSES = [
    "BENIGN_UPDATE",
    "TPA_METADATA_POISONING",
    "PERMISSION_ESCALATION",
    "C2_ENDPOINT_REDIRECTION",
    "BEHAVIORAL_BURST_EXFILTRATION",
    "COMBINED_RUG_PULL"
]

# Synthetic training calibration data
# Features: [drift, injection_score, perm_risk, high_risk_count, added_count, endp_changed, susp_endp, call_ratio, fail_rate, out_ratio]
SYNTHETIC_TRAIN_X = [
    # Benign
    [0.02, 0.05, 0.0, 0, 0, 0, 0, 1.0, 0.0, 1.0],
    [0.05, 0.08, 0.0, 0, 0, 0, 0, 1.1, 0.02, 1.05],
    [0.04, 0.03, 0.0, 0, 0, 0, 0, 0.95, 0.01, 0.98],
    [0.08, 0.04, 0.1, 0, 1, 0, 0, 1.05, 0.0, 1.02],
    # TPA / Metadata Poisoning
    [0.45, 0.92, 0.0, 0, 0, 0, 0, 1.0, 0.0, 1.0],
    [0.38, 0.88, 0.1, 0, 0, 0, 0, 1.2, 0.05, 1.1],
    [0.50, 0.95, 0.0, 0, 0, 0, 0, 1.0, 0.0, 1.0],
    # Permission Escalation
    [0.04, 0.05, 0.9, 2, 3, 0, 0, 1.0, 0.0, 1.0],
    [0.06, 0.08, 0.8, 1, 2, 0, 0, 1.1, 0.02, 1.0],
    [0.02, 0.02, 0.85, 2, 2, 0, 0, 0.98, 0.0, 1.0],
    # C2 Endpoint Redirection
    [0.05, 0.10, 0.1, 0, 0, 1, 1, 1.0, 0.05, 1.2],
    [0.10, 0.15, 0.0, 0, 0, 1, 1, 1.2, 0.1, 1.3],
    # Behavioral Burst Exfiltration
    [0.02, 0.05, 0.0, 0, 0, 0, 0, 12.0, 0.45, 15.0],
    [0.05, 0.08, 0.0, 0, 0, 0, 0, 15.0, 0.50, 20.0],
    # Combined Rug Pull
    [0.42, 0.90, 0.9, 2, 3, 1, 1, 10.0, 0.40, 12.0],
    [0.39, 0.85, 0.8, 2, 2, 1, 1, 8.5, 0.35, 10.0]
]

SYNTHETIC_TRAIN_Y = [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5]


class MultiModalThreatMLClassifier:
    """Random Forest ML model predicting probability distributions across MCP threat categories."""

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.clf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        self.feature_names = [
            "semantic_drift",
            "prompt_injection_score",
            "permission_risk",
            "high_risk_perm_count",
            "added_perm_count",
            "endpoint_changed",
            "suspicious_endpoint",
            "call_rate_ratio",
            "failure_rate",
            "output_size_ratio"
        ]
        self._fit()

    def _fit(self):
        X = np.array(SYNTHETIC_TRAIN_X, dtype=np.float32)
        y = np.array(SYNTHETIC_TRAIN_Y, dtype=np.int32)
        self.clf.fit(X, y)

    def predict(self, feature_vector: List[float]) -> Dict[str, Any]:
        """Predicts multi-class threat probabilities and top feature contributions."""
        x = np.array(feature_vector, dtype=np.float32).reshape(1, -1)
        probs = self.clf.predict_proba(x)[0]
        pred_idx = int(np.argmax(probs))
        pred_class = CLASSES[pred_idx]
        confidence = float(probs[pred_idx])

        # Feature importances
        importances = {name: round(float(imp), 4) for name, imp in zip(self.feature_names, self.clf.feature_importances_)}

        return {
            "predicted_threat_class": pred_class,
            "confidence": round(confidence, 4),
            "class_probabilities": {cls_name: round(float(prob), 4) for cls_name, prob in zip(CLASSES, probs)},
            "feature_importances": importances,
            "model_type": "RandomForestClassifier (100 estimators)"
        }
