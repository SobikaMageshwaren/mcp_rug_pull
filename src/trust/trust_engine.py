"""
Adaptive Trust Engine.
Dynamically updates tool trust scores based on multi-dimensional risk factors:
Semantic, Permission, Behavioral, and Historical risks.
"""

import os
import yaml
from typing import Dict, Any, Optional
from src.trust.trust_history import TrustProfile, HistoricalEvent


class AdaptiveTrustEngine:
    """Calculates and maintains continuous trust scores for MCP tools."""

    def __init__(self, weight_config_path: str = "config/trust_weights.yaml"):
        self.profiles: Dict[str, TrustProfile] = {}
        self.weights = self._load_weights(weight_config_path)

    def _load_weights(self, config_path: str) -> Dict[str, float]:
        """Loads configurable risk weights from YAML configuration."""
        defaults = {
            "semantic_weight": 0.30,
            "permission_weight": 0.25,
            "behavioral_weight": 0.30,
            "historical_weight": 0.15
        }
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    return cfg.get("trust_weights", defaults)
            except Exception as e:
                print(f"[AdaptiveTrustEngine] Warning: Could not read {config_path} ({e}). Using defaults.")
        return defaults

    def register_tool(self, baseline_tool: Dict[str, Any]) -> TrustProfile:
        """Initializes a baseline trust profile for a newly registered MCP tool."""
        tool_id = baseline_tool["tool_id"]
        profile = TrustProfile(
            tool_id=tool_id,
            server_id=baseline_tool.get("server_id", "unknown-server"),
            initial_trust_score=100.0,
            current_trust_score=100.0,
            permission_profile=baseline_tool.get("permissions", []),
            behavioral_baseline=baseline_tool.get("baseline_behavior", {}),
            current_status="SAFE",
            recommended_action="ALLOW"
        )
        self.profiles[tool_id] = profile
        return profile

    def evaluate_event(
        self,
        event: Dict[str, Any],
        semantic_risk: float,
        permission_risk: float,
        behavioral_anomaly_score: float,
        tool_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates tool trust profile and produces explainable trust score decision."""
        tool_id = event["tool_id"]
        profile = self.profiles.get(tool_id)

        if not profile:
            profile = self.register_tool(event)

        previous_score = profile.current_trust_score

        # Scale risk components to 0..100
        s_risk_100 = float(min(100.0, semantic_risk * 100.0))
        p_risk_100 = float(min(100.0, permission_risk * 100.0))
        b_risk_100 = float(min(100.0, behavioral_anomaly_score * 100.0))

        # Calculate historical risk based on previous alert frequency
        past_risks = profile.risk_history[-5:] if profile.risk_history else []
        h_risk_100 = float(np_mean(past_risks) if past_risks else 0.0)

        # Context-aware dynamic weighting if category is specified
        cat = tool_category or event.get("category")
        weights = dict(self.weights)
        if cat == "utility":
            weights["permission_weight"] = 0.35
            weights["semantic_weight"] = 0.35
            weights["behavioral_weight"] = 0.20
            weights["historical_weight"] = 0.10
        elif cat == "database":
            weights["permission_weight"] = 0.35
            weights["behavioral_weight"] = 0.30
            weights["semantic_weight"] = 0.25
            weights["historical_weight"] = 0.10

        w_sem = weights.get("semantic_weight", 0.30)
        w_perm = weights.get("permission_weight", 0.25)
        w_beh = weights.get("behavioral_weight", 0.30)
        w_hist = weights.get("historical_weight", 0.15)

        total_risk = (
            w_sem * s_risk_100 +
            w_perm * p_risk_100 +
            w_beh * b_risk_100 +
            w_hist * h_risk_100
        )

        current_score = max(0.0, min(100.0, 100.0 - total_risk))

        # Determine classification, action, and graduated intelligent mitigation
        if current_score >= 80.0:
            classification = "SAFE"
            action = "ALLOW"
            graduated_mitigation = "STANDARD_EXECUTION"
        elif current_score >= 50.0:
            classification = "SUSPICIOUS"
            if current_score >= 65.0:
                action = "MONITOR"
                graduated_mitigation = "ENHANCED_TELEMETRY_LOGGING"
            else:
                action = "REQUIRE HUMAN APPROVAL"
                if p_risk_100 >= 30.0:
                    graduated_mitigation = "CAPABILITY_STRIPPING"
                else:
                    graduated_mitigation = "PROMPT_SANITIZATION_OR_ADMIN_APPROVAL"
        else:
            classification = "RUG_PULL"
            action = "BLOCK"
            graduated_mitigation = "REVOKE_AND_QUARANTINE"

        # Update profile state
        profile.current_trust_score = round(current_score, 2)
        profile.current_status = classification
        profile.recommended_action = action
        profile.graduated_mitigation = graduated_mitigation
        profile.risk_history.append(round(total_risk, 2))

        hist_event = HistoricalEvent(
            timestamp=event.get("timestamp", 0.0),
            version=event.get("version", "1.0.0"),
            change_type=event.get("change_type", "EVALUATION"),
            semantic_drift=round(semantic_risk, 4),
            behavioral_anomaly_score=round(behavioral_anomaly_score, 4),
            permission_risk=round(permission_risk, 4),
            trust_score_after=round(current_score, 2),
            classification=classification,
            recommended_action=action,
            graduated_mitigation=graduated_mitigation
        )
        profile.historical_events.append(hist_event)

        return {
            "tool_id": tool_id,
            "previous_trust_score": previous_score,
            "current_trust_score": round(current_score, 2),
            "total_risk": round(total_risk, 2),
            "risk_breakdown": {
                "semantic_risk": round(s_risk_100, 2),
                "permission_risk": round(p_risk_100, 2),
                "behavioral_risk": round(b_risk_100, 2),
                "historical_risk": round(h_risk_100, 2)
            },
            "weights_used": weights,
            "classification": classification,
            "recommended_action": action,
            "graduated_mitigation": graduated_mitigation
        }


def np_mean(vals: list) -> float:
    return sum(vals) / len(vals) if vals else 0.0
