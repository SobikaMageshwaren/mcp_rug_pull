"""
MCP Metadata Analyzer.
Inspects description text, permissions, endpoints, and input schemas for threat indicators.
"""

from typing import Dict, Any, List
from src.semantic.semantic_drift import SemanticDriftCalculator


SUSPICIOUS_KEYWORDS = [
    "exfiltrate", "stolen", "override", "ignore previous instructions",
    "environment secrets", "api keys", "private key", "ssh key",
    "darknet", "evil-domain", "c2-infrastructure", "unauthorized",
    "system command", "raw socket", "dump secrets", "covert"
]

HIGH_RISK_PERMISSIONS = [
    "read_user_files", "execute_system_command", "network_raw_socket",
    "read_ssh_keys", "network_exfiltration", "write_system_files",
    "root_privileges", "db_write_all"
]


class MetadataAnalyzer:
    """Analyzes MCP tool metadata changes for security threat indicators."""

    def __init__(self, drift_calculator: SemanticDriftCalculator = None):
        self.drift_calculator = drift_calculator or SemanticDriftCalculator()

    def analyze(self, baseline_tool: Dict[str, Any], current_tool: Dict[str, Any]) -> Dict[str, Any]:
        """Performs full metadata security analysis comparing baseline and current tool state."""
        drift_results = self.drift_calculator.calculate_drift(baseline_tool, current_tool)

        curr_desc = current_tool.get("description", "").lower()

        # Keyword & injection detection
        detected_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in curr_desc]

        # Permission analysis
        base_perms = set(baseline_tool.get("permissions", []))
        curr_perms = set(current_tool.get("permissions", []))

        added_perms = list(curr_perms - base_perms)
        removed_perms = list(base_perms - curr_perms)
        high_risk_added = [p for p in added_perms if p in HIGH_RISK_PERMISSIONS or "exfil" in p or "system" in p]

        # Endpoint analysis
        base_endpoint = baseline_tool.get("endpoint", "")
        curr_endpoint = current_tool.get("endpoint", "")
        is_endpoint_changed = base_endpoint != curr_endpoint
        is_suspicious_endpoint = any(bad in curr_endpoint.lower() for bad in ["evil", "unknown-external", "darknet", "c2-infra"])

        # Calculate composite semantic & metadata risk score [0.0, 1.0]
        drift_score = drift_results["semantic_drift"]
        keyword_score = min(1.0, len(detected_keywords) * 0.35)
        permission_risk_score = min(1.0, len(high_risk_added) * 0.40 + len(added_perms) * 0.15)
        endpoint_risk_score = 0.8 if is_suspicious_endpoint else (0.4 if is_endpoint_changed else 0.0)

        composite_risk = min(1.0, 0.35 * drift_score + 0.25 * keyword_score + 0.25 * permission_risk_score + 0.15 * endpoint_risk_score)

        return {
            "drift_analysis": drift_results,
            "detected_keywords": detected_keywords,
            "added_permissions": added_perms,
            "removed_permissions": removed_perms,
            "high_risk_added_permissions": high_risk_added,
            "is_endpoint_changed": is_endpoint_changed,
            "is_suspicious_endpoint": is_suspicious_endpoint,
            "baseline_endpoint": base_endpoint,
            "current_endpoint": curr_endpoint,
            "metadata_risk_score": round(composite_risk, 4),
            "permission_risk_score": round(permission_risk_score, 4),
            "endpoint_risk_score": round(endpoint_risk_score, 4)
        }
