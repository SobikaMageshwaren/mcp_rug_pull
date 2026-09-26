"""
Behavioral Anomaly Detector.
Trains IsolationForest, One-Class SVM, or LocalOutlierFactor models on benign tool behavior.
Computes calibrated anomaly scores [0.0, 1.0].
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from src.behavioral.feature_extractor import BehavioralFeatureExtractor


class BehavioralAnomalyDetector:
    """Unsupervised behavioral anomaly detector using Isolation Forest and scaling."""

    def __init__(self, algorithm: str = "IsolationForest", contamination: float = 0.15, random_state: int = 42):
        self.algorithm = algorithm
        self.contamination = contamination
        self.random_state = random_state
        self.extractor = BehavioralFeatureExtractor()
        self.scaler = StandardScaler()
        self.is_fitted = False

        if algorithm == "IsolationForest":
            self.model = IsolationForest(
                n_estimators=100,
                contamination=contamination,
                random_state=random_state
            )
        elif algorithm == "OneClassSVM":
            self.model = OneClassSVM(nu=contamination, kernel="rbf", gamma="scale")
        elif algorithm == "LocalOutlierFactor":
            self.model = LocalOutlierFactor(n_neighbors=20, contamination=contamination, novelty=True)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def fit(self, benign_events: List[Dict[str, Any]], baseline_map: Dict[str, Dict[str, Any]] = None):
        """Fits feature scaler and anomaly model on benign operational events."""
        X = self.extractor.extract_batch(benign_events, baseline_map)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
        return self

    def predict_anomaly_score(self, event: Dict[str, Any], baseline_tool: Dict[str, Any] = None) -> float:
        """Computes calibrated anomaly score in range [0.0, 1.0]."""
        if not self.is_fitted:
            # Fallback heuristic score if model unfitted
            return self._heuristic_score(event, baseline_tool)

        vec = self.extractor.extract_features(event, baseline_tool).reshape(1, -1)
        vec_scaled = self.scaler.transform(vec)

        if self.algorithm == "IsolationForest":
            # decision_function gives negative values for anomalies, positive for inliers
            raw_score = self.model.decision_function(vec_scaled)[0]
            # Convert raw score to 0..1 scale (lower decision_function = higher anomaly)
            anomaly_score = 1.0 - (1.0 / (1.0 + np.exp(-raw_score * 4.0)))
        elif self.algorithm in ["OneClassSVM", "LocalOutlierFactor"]:
            raw_score = self.model.decision_function(vec_scaled)[0]
            anomaly_score = 1.0 - (1.0 / (1.0 + np.exp(-raw_score * 3.0)))
        else:
            anomaly_score = 0.5

        return float(np.clip(anomaly_score, 0.0, 1.0))

    def _heuristic_score(self, event: Dict[str, Any], baseline_tool: Dict[str, Any] = None) -> float:
        """Heuristic behavioral risk calculation when ML model is not yet trained."""
        beh = event.get("baseline_behavior", {})
        base_beh = baseline_tool.get("baseline_behavior", {}) if baseline_tool else {}

        call_ratio = beh.get("calls_per_minute", 5.0) / max(1.0, base_beh.get("calls_per_minute", 5.0))
        fail_rate = beh.get("failure_rate", 0.0)

        score = 0.0
        if call_ratio > 3.0:
            score += 0.4
        if fail_rate > 0.2:
            score += 0.4
        return float(min(1.0, score))
