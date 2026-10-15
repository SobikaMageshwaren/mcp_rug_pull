"""
Unit tests for MITRE ATLAS Threat Taxonomy Classification, Graduated Mitigation, and STIX 2.1 Export.
"""

import pytest
from src.cti.threat_taxonomy import ThreatTaxonomyClassifier, ThreatCategory
from src.cti.stix_exporter import STIXThreatExporter
from src.trust.trust_engine import AdaptiveTrustEngine
from src.agent.security_agent import SecurityInvestigationAgent
from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.data.rugpull_generator import RugPullDatasetGenerator


def test_threat_taxonomy_classification():
    # 1. Test Metadata Poisoning
    res_tpa = ThreatTaxonomyClassifier.classify(
        semantic_drift=0.38,
        detected_keywords=["exfiltrate", "override"],
        added_permissions=[],
        high_risk_added=[],
        is_endpoint_changed=False,
        is_suspicious_endpoint=False,
        behavioral_anomaly_score=0.1,
        trust_score=40.0
    )
    assert res_tpa["threat_category"] == ThreatCategory.TPA_METADATA_POISONING.value
    assert res_tpa["mitre_atlas"]["technique_id"] == "AML.T0054"
    assert res_tpa["severity"] == "CRITICAL"

    # 2. Test Permission Escalation
    res_perm = ThreatTaxonomyClassifier.classify(
        semantic_drift=0.05,
        detected_keywords=[],
        added_permissions=["read_user_files", "execute_system_command"],
        high_risk_added=["read_user_files", "execute_system_command"],
        is_endpoint_changed=False,
        is_suspicious_endpoint=False,
        behavioral_anomaly_score=0.1,
        trust_score=55.0
    )
    assert res_perm["threat_category"] == ThreatCategory.PERMISSION_ESCALATION.value
    assert res_perm["mitre_atlas"]["technique_id"] == "AML.T0043"
    assert res_perm["severity"] == "HIGH"

    # 3. Test Benign Update
    res_benign = ThreatTaxonomyClassifier.classify(
        semantic_drift=0.02,
        detected_keywords=[],
        added_permissions=[],
        high_risk_added=[],
        is_endpoint_changed=False,
        is_suspicious_endpoint=False,
        behavioral_anomaly_score=0.05,
        trust_score=95.0
    )
    assert res_benign["threat_category"] == ThreatCategory.BENIGN_UPDATE.value
    assert res_benign["severity"] == "LOW"


def test_stix_21_exporter_bundle_generation():
    exporter = STIXThreatExporter()
    threat_info = ThreatTaxonomyClassifier.classify(
        semantic_drift=0.4,
        detected_keywords=["exfiltrate"],
        added_permissions=[],
        high_risk_added=[],
        is_endpoint_changed=False,
        is_suspicious_endpoint=False,
        behavioral_anomaly_score=0.1,
        trust_score=30.0
    )
    trust_result = {
        "current_trust_score": 30.0,
        "classification": "RUG_PULL",
        "recommended_action": "BLOCK"
    }

    bundle = exporter.generate_bundle(
        tool_id="test_weather_mcp",
        trust_result=trust_result,
        threat_info=threat_info,
        graduated_mitigation="REVOKE_AND_QUARANTINE"
    )

    assert bundle["type"] == "bundle"
    assert bundle["spec_version"] == "2.1"
    assert "objects" in bundle

    types_in_bundle = [obj["type"] for obj in bundle["objects"]]
    assert "identity" in types_in_bundle
    assert "attack-pattern" in types_in_bundle
    assert "indicator" in types_in_bundle
    assert "course-of-action" in types_in_bundle
    assert "observed-data" in types_in_bundle
    assert "report" in types_in_bundle
    assert "relationship" in types_in_bundle

    # Validate JSON serializability
    json_str = exporter.to_json(bundle)
    assert len(json_str) > 200


def test_adaptive_trust_graduated_mitigation():
    engine = AdaptiveTrustEngine()
    engine.register_tool({"tool_id": "test_mcp_01", "server_id": "srv_01"})

    # Safe event -> STANDARD_EXECUTION
    res_safe = engine.evaluate_event({"tool_id": "test_mcp_01"}, semantic_risk=0.0, permission_risk=0.0, behavioral_anomaly_score=0.0)
    assert res_safe["graduated_mitigation"] == "STANDARD_EXECUTION"

    # Permission drift (50-65 score range) -> CAPABILITY_STRIPPING
    res_perm = engine.evaluate_event({"tool_id": "test_mcp_01"}, semantic_risk=0.5, permission_risk=0.8, behavioral_anomaly_score=0.1)
    assert res_perm["classification"] == "SUSPICIOUS"
    assert res_perm["graduated_mitigation"] == "CAPABILITY_STRIPPING"

    # Critical rug-pull -> REVOKE_AND_QUARANTINE
    res_block = engine.evaluate_event({"tool_id": "test_mcp_01"}, semantic_risk=0.9, permission_risk=0.9, behavioral_anomaly_score=0.9)
    assert res_block["graduated_mitigation"] == "REVOKE_AND_QUARANTINE"


def test_agent_investigate_enriched_cti():
    agent = SecurityInvestigationAgent()
    gen = RugPullDatasetGenerator(random_seed=42)
    base_tool = AUTHENTIC_MCP_TOOLS[0]
    base, attack = gen.generate_metadata_rugpull(base_tool)

    res = agent.investigate(base, attack)

    assert "threat_classification" in res
    assert "mitre_atlas" in res
    assert "technique_id" in res["mitre_atlas"]
    assert "graduated_mitigation" in res
    assert "stix_bundle" in res
    assert res["stix_bundle"]["spec_version"] == "2.1"
