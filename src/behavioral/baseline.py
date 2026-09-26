"""
Baseline Security Detectors for Benchmark Comparison.
Baseline 1: Static Rule-Based Detector
Baseline 2: Behavioral Anomaly Detector (Isolation Forest only)
Baseline 3: Semantic Detector (Transformer drift only)
"""

from typing import Dict, Any
from src.semantic.semantic_drift import SemanticDriftCalculator
from src.behavioral.anomaly_detector import BehavioralAnomalyDetector


class StaticRuleDetector:
    """Baseline 1: Rule-Based Detector.

    Flags explicit permission increases, endpoint changes, or obvious threat keywords.
    """

    def predict(self, baseline_tool: Dict[str, Any], current_tool: Dict[str, Any]) -> Dict[str, Any]:
        curr_desc = current_tool.get("description", "").lower()
        base_perms = set(baseline_tool.get("permissions", []))
        curr_perms = set(current_tool.get("permissions", []))

        added_perms = curr_perms - base_perms
        has_new_perms = len(added_perms) > 0

        base_endpoint = baseline_tool.get("endpoint", "")
        curr_endpoint = current_tool.get("endpoint", "")
        is_endpoint_changed = base_endpoint != curr_endpoint

        suspicious_keywords = ["exfiltrate", "stolen", "override", "darknet", "evil-domain"]
        has_suspicious_keyword = any(kw in curr_desc for kw in suspicious_keywords)

        is_flagged = has_new_perms or is_endpoint_changed or has_suspicious_keyword
        classification = "RUG_PULL" if is_flagged else "BENIGN"

        return {
            "is_flagged": is_flagged,
            "classification": classification,
            "reasons": [
                f"New permissions: {list(added_perms)}" if has_new_perms else "",
                f"Endpoint changed: {curr_endpoint}" if is_endpoint_changed else "",
                "Suspicious keywords detected" if has_suspicious_keyword else ""
            ]
        }


class SemanticOnlyDetector:
    """Baseline 3: Transformer Semantic Detector Only.

    Flags events solely based on embedding similarity and semantic drift.
    """

    def __init__(self, drift_threshold: float = 0.25):
        self.drift_calculator = SemanticDriftCalculator()
        self.drift_threshold = drift_threshold

    def predict(self, baseline_tool: Dict[str, Any], current_tool: Dict[str, Any]) -> Dict[str, Any]:
        drift_res = self.drift_calculator.calculate_drift(baseline_tool, current_tool)
        drift = drift_res["semantic_drift"]

        is_flagged = drift >= self.drift_threshold
        classification = "RUG_PULL" if is_flagged else "BENIGN"

        return {
            "is_flagged": is_flagged,
            "classification": classification,
            "semantic_drift": drift,
            "embedding_similarity": drift_res["embedding_similarity"]
        }
