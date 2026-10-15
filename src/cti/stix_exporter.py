"""
STIX 2.1 Cyber Threat Intelligence Exporter for TrustGuard-MCP.
Generates OASIS STIX 2.1 JSON compliant incident bundles for identified MCP rug-pull attacks.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class STIXThreatExporter:
    """Exports TrustGuard-MCP incident investigations as OASIS STIX 2.1 standardized bundles."""

    def __init__(self, organization_name: str = "TrustGuard-MCP CTI Monitor"):
        self.organization_name = organization_name
        self.identity_id = f"identity--{uuid.uuid5(uuid.NAMESPACE_DNS, 'trustguard-mcp.org')}"

    def generate_bundle(
        self,
        tool_id: str,
        trust_result: Dict[str, Any],
        threat_info: Dict[str, Any],
        graduated_mitigation: str,
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generates a valid STIX 2.1 JSON bundle structure."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        bundle_id = f"bundle--{uuid.uuid4()}"

        # 1. Identity Object
        identity_obj = {
            "type": "identity",
            "spec_version": "2.1",
            "id": self.identity_id,
            "created": now_iso,
            "modified": now_iso,
            "name": self.organization_name,
            "identity_class": "system",
            "sectors": ["technology", "defense"]
        }

        # 2. Attack Pattern Object (MITRE ATLAS / ATT&CK)
        atlas = threat_info.get("mitre_atlas", {})
        attack_pattern_id = f"attack-pattern--{uuid.uuid4()}"
        attack_pattern_obj = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": attack_pattern_id,
            "created": now_iso,
            "modified": now_iso,
            "name": threat_info.get("threat_name", "MCP Tool Rug-Pull"),
            "description": threat_info.get("threat_description", "Post-approval staged trust erosion on MCP tool schema."),
            "external_references": [
                {
                    "source_name": "mitre-atlas",
                    "external_id": atlas.get("technique_id", "AML.T0054"),
                    "url": atlas.get("url", "https://atlas.mitre.org")
                }
            ]
        }

        # 3. Indicator Object
        indicator_id = f"indicator--{uuid.uuid4()}"
        indicator_obj = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": indicator_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"Indicator for MCP tool {tool_id}",
            "description": f"Trust degraded to {trust_result.get('current_trust_score', 0.0)}. Threat: {threat_info.get('threat_category')}",
            "indicator_types": ["malicious-activity", "anomalous-activity"],
            "pattern": f"[file:name = '{tool_id}']",
            "pattern_type": "stix",
            "valid_from": now_iso,
            "confidence": 85 if threat_info.get("severity") in ["HIGH", "CRITICAL"] else 60
        }

        # 4. Course of Action Object (Mitigation)
        coa_id = f"course-of-action--{uuid.uuid4()}"
        coa_obj = {
            "type": "course-of-action",
            "spec_version": "2.1",
            "id": coa_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"Policy Enforcement: {graduated_mitigation}",
            "description": f"Enforce {trust_result.get('recommended_action', 'BLOCK')} ({graduated_mitigation}) on tool {tool_id}."
        }

        # 5. Observed Data Object
        observed_id = f"observed-data--{uuid.uuid4()}"
        observed_obj = {
            "type": "observed-data",
            "spec_version": "2.1",
            "id": observed_id,
            "created": now_iso,
            "modified": now_iso,
            "first_observed": now_iso,
            "last_observed": now_iso,
            "number_observed": 1,
            "objects": {
                "0": {
                    "type": "process",
                    "command_line": f"mcp://{tool_id}",
                    "x_trust_score": trust_result.get("current_trust_score", 0.0),
                    "x_semantic_drift": trust_result.get("semantic_drift", 0.0),
                    "x_permission_risk": trust_result.get("permission_risk", 0.0),
                    "x_behavioral_score": trust_result.get("behavioral_anomaly_score", 0.0)
                }
            }
        }

        # 6. Relationships
        rel_indicates = {
            "type": "relationship",
            "spec_version": "2.1",
            "id": f"relationship--{uuid.uuid4()}",
            "created": now_iso,
            "modified": now_iso,
            "relationship_type": "indicates",
            "source_ref": indicator_id,
            "target_ref": attack_pattern_id
        }

        rel_mitigates = {
            "type": "relationship",
            "spec_version": "2.1",
            "id": f"relationship--{uuid.uuid4()}",
            "created": now_iso,
            "modified": now_iso,
            "relationship_type": "mitigates",
            "source_ref": coa_id,
            "target_ref": attack_pattern_id
        }

        # 7. Report Object
        object_refs = [
            self.identity_id,
            attack_pattern_id,
            indicator_id,
            coa_id,
            observed_id,
            rel_indicates["id"],
            rel_mitigates["id"]
        ]

        report_id = f"report--{uuid.uuid4()}"
        report_obj = {
            "type": "report",
            "spec_version": "2.1",
            "id": report_id,
            "created": now_iso,
            "modified": now_iso,
            "name": f"TrustGuard-MCP CTI Incident Report: {tool_id}",
            "description": f"Automated Security Incident Report for tool '{tool_id}'. Security Status: {trust_result.get('classification')}, Mitigated by: {graduated_mitigation}.",
            "published": now_iso,
            "report_types": ["threat-report", "vulnerability"],
            "object_refs": object_refs
        }

        stix_objects = [
            identity_obj,
            attack_pattern_obj,
            indicator_obj,
            coa_obj,
            observed_obj,
            rel_indicates,
            rel_mitigates,
            report_obj
        ]

        return {
            "type": "bundle",
            "id": bundle_id,
            "spec_version": "2.1",
            "objects": stix_objects
        }

    def to_json(self, bundle: Dict[str, Any], indent: int = 2) -> str:
        """Serializes bundle into formatted JSON string."""
        return json.dumps(bundle, indent=indent)
