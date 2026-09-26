"""
Behavioral Feature Extractor.
Converts raw tool event metadata and runtime observations into normalized feature vectors for ML models.
"""

import numpy as np
from typing import Dict, Any, List


FEATURE_NAMES = [
    "calls_per_minute",
    "failure_rate",
    "average_latency",
    "latency_std",
    "unique_domains_count",
    "new_domains_count",
    "parameter_change_count",
    "permission_count",
    "sensitive_access_count",
    "output_length_mean",
    "output_length_std"
]

HIGH_RISK_PERM_LIST = [
    "read_user_files", "execute_system_command", "network_raw_socket",
    "read_ssh_keys", "network_exfiltration", "write_system_files"
]


class BehavioralFeatureExtractor:
    """Extracts numerical feature arrays from MCP tool events for anomaly detection."""

    def __init__(self):
        self.feature_names = FEATURE_NAMES

    def extract_features(self, event: Dict[str, Any], baseline_tool: Dict[str, Any] = None) -> np.ndarray:
        """Transforms a single tool event into a 1D float numpy array."""
        beh = event.get("baseline_behavior", {})

        calls_per_min = float(beh.get("calls_per_minute", 5.0))
        fail_rate = float(beh.get("failure_rate", 0.0))
        avg_lat = float(beh.get("average_latency_ms", 100.0))
        lat_std = float(beh.get("latency_std_ms", 15.0))

        domains = beh.get("unique_domains", [])
        unique_dom_count = float(len(domains))

        # Check domain shifts relative to baseline
        base_domains = set(baseline_tool.get("baseline_behavior", {}).get("unique_domains", [])) if baseline_tool else set()
        new_dom_count = float(len(set(domains) - base_domains)) if base_domains else 0.0

        # Parameters & Schema properties count
        params = event.get("input_schema", {}).get("properties", {})
        param_count = float(len(params))

        # Permissions count & Sensitive permissions count
        perms = event.get("permissions", [])
        perm_count = float(len(perms))
        sens_count = float(sum(1 for p in perms if p in HIGH_RISK_PERM_LIST or "exfil" in p or "system" in p))

        # Output payload statistics
        out_mean = float(beh.get("output_length_mean", 500.0))
        out_std = float(beh.get("output_length_std", 50.0))

        vec = np.array([
            calls_per_min,
            fail_rate,
            avg_lat,
            lat_std,
            unique_dom_count,
            new_dom_count,
            param_count,
            perm_count,
            sens_count,
            out_mean,
            out_std
        ], dtype=np.float64)

        return vec

    def extract_batch(self, events: List[Dict[str, Any]], baseline_map: Dict[str, Dict[str, Any]] = None) -> np.ndarray:
        """Extracts feature matrix (N, num_features) from a list of events."""
        rows = []
        for event in events:
            tool_id = event.get("tool_id")
            base = baseline_map.get(tool_id) if baseline_map else None
            rows.append(self.extract_features(event, base))
        return np.vstack(rows)
