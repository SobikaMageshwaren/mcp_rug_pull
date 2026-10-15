"""
Security Investigation Agent.
Autonomous agentic investigator that orchestrates tool calls to investigate suspicious MCP events.
"""

from typing import Dict, Any, List
from src.agent.tools import InvestigationTools
from src.trust.trust_engine import AdaptiveTrustEngine
from src.behavioral.anomaly_detector import BehavioralAnomalyDetector
from src.semantic.metadata_analyzer import MetadataAnalyzer
from src.rag.retriever import CTIThreatRetriever


class SecurityInvestigationAgent:
    """Agentic security investigator executing multi-tool investigation workflow."""

    def __init__(
        self,
        trust_engine: AdaptiveTrustEngine = None,
        anomaly_detector: BehavioralAnomalyDetector = None,
        metadata_analyzer: MetadataAnalyzer = None,
        threat_retriever: CTIThreatRetriever = None
    ):
        self.tools = InvestigationTools(
            trust_engine=trust_engine,
            anomaly_detector=anomaly_detector,
            metadata_analyzer=metadata_analyzer,
            threat_retriever=threat_retriever
        )

    def investigate(self, baseline_tool: Dict[str, Any], current_event: Dict[str, Any]) -> Dict[str, Any]:
        """Runs autonomous end-to-end security investigation workflow."""
        tool_id = current_event["tool_id"]
        invoked_tools = []
        evidence = []

        # 1. Inspect metadata changes and semantic drift
        invoked_tools.append("compare_tool_versions")
        meta_res = self.tools.compare_tool_versions(baseline_tool, current_event)["comparison"]
        drift_val = meta_res["drift_analysis"]["semantic_drift"]
        metadata_risk = meta_res["metadata_risk_score"]

        if meta_res["drift_analysis"]["is_description_changed"]:
            evidence.append(f"Tool description changed (semantic drift: {drift_val:.2f})")
        if meta_res["detected_keywords"]:
            evidence.append(f"Suspicious threat keywords detected: {meta_res['detected_keywords']}")
        if meta_res["is_suspicious_endpoint"]:
            evidence.append(f"Outbound endpoint routed to suspicious domain: {current_event.get('endpoint')}")

        # 2. Inspect permission changes
        invoked_tools.append("inspect_permissions")
        perm_res = self.tools.inspect_permissions(baseline_tool, current_event)
        perm_risk = meta_res["permission_risk_score"]

        if perm_res["added_permissions"]:
            evidence.append(f"Added permissions: {perm_res['added_permissions']}")
        if perm_res["high_risk_added"]:
            evidence.append(f"DANGEROUS privilege escalation: {perm_res['high_risk_added']}")

        # 3. Analyze runtime behavior anomalies
        invoked_tools.append("get_behavior_history")
        beh_res = self.tools.get_behavior_history(current_event, baseline_tool)
        beh_score = beh_res["behavioral_anomaly_score"]

        if beh_res["is_anomalous"]:
            evidence.append(f"Runtime behavioral anomaly detected (anomaly score: {beh_score:.2f})")

        # 4. Query RAG Threat Intelligence
        invoked_tools.append("search_threat_intelligence")
        query = f"MCP tool {tool_id} " + " ".join(evidence)
        rag_res = self.tools.search_threat_intelligence(query, top_k=2)
        threat_intel = rag_res["threat_intelligence"]

        # 5. Calculate Adaptive Trust Score
        invoked_tools.append("calculate_trust_score")
        category = current_event.get("category") or baseline_tool.get("category")
        trust_res = self.tools.calculate_trust_score(current_event, metadata_risk, perm_risk, beh_score)["trust_evaluation"]

        # 6. Multi-Class CTI Threat Classification (MITRE ATLAS & ATT&CK)
        invoked_tools.append("classify_threat")
        threat_info = self.tools.classify_threat(
            semantic_drift=drift_val,
            detected_keywords=meta_res.get("detected_keywords", []),
            added_permissions=perm_res.get("added_permissions", []),
            high_risk_added=perm_res.get("high_risk_added", []),
            is_endpoint_changed=meta_res.get("is_endpoint_changed", False),
            is_suspicious_endpoint=meta_res.get("is_suspicious_endpoint", False),
            behavioral_anomaly_score=beh_score,
            trust_score=trust_res["current_trust_score"]
        )

        graduated_mitigation = trust_res.get("graduated_mitigation", "STANDARD_EXECUTION")

        # 7. Generate STIX 2.1 Threat Intelligence Bundle
        invoked_tools.append("export_stix_bundle")
        stix_bundle = self.tools.export_stix_bundle(
            tool_id=tool_id,
            trust_result=trust_res,
            threat_info=threat_info,
            graduated_mitigation=graduated_mitigation,
            citations=threat_intel
        )

        # 8. Generate final explainable security report
        invoked_tools.append("generate_security_report")
        report = self.tools.generate_security_report(
            tool_id=tool_id,
            classification=trust_res["classification"],
            recommended_action=trust_res["recommended_action"],
            evidence=evidence,
            threat_intelligence=threat_intel,
            threat_info=threat_info,
            graduated_mitigation=graduated_mitigation
        )

        return {
            "tool_id": tool_id,
            "previous_trust_score": trust_res["previous_trust_score"],
            "current_trust_score": trust_res["current_trust_score"],
            "semantic_drift": drift_val,
            "behavioral_anomaly_score": beh_score,
            "permission_risk": perm_risk,
            "classification": trust_res["classification"],
            "recommended_action": trust_res["recommended_action"],
            "graduated_mitigation": graduated_mitigation,
            "threat_classification": threat_info["threat_category"],
            "threat_name": threat_info["threat_name"],
            "severity": threat_info["severity"],
            "mitre_atlas": threat_info["mitre_atlas"],
            "mitre_attack": threat_info["mitre_attack"],
            "stix_bundle": stix_bundle,
            "evidence": evidence if evidence else ["Tool behavior and metadata match benign baseline."],
            "threat_intelligence": threat_intel,
            "invoked_tools": invoked_tools,
            "explanation": [
                f"Previous trust score: {trust_res['previous_trust_score']}, Current trust score: {trust_res['current_trust_score']}",
                f"Classification: {trust_res['classification']}, Recommended action: {trust_res['recommended_action']}, Graduated mitigation: {graduated_mitigation}",
                f"Threat taxonomy: {threat_info['threat_name']} (MITRE ATLAS: {threat_info['mitre_atlas']['technique_id']})",
                f"Risk components -> Semantic: {trust_res['risk_breakdown']['semantic_risk']}, Permission: {trust_res['risk_breakdown']['permission_risk']}, Behavioral: {trust_res['risk_breakdown']['behavioral_risk']}"
            ]
        }

