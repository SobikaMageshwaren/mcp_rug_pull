"""
Investigation Tools for Security Investigation Agent.
Callable python functions provided to the security agent for evidence collection and reasoning.
"""

from typing import Dict, Any, List, Optional
from src.semantic.metadata_analyzer import MetadataAnalyzer
from src.semantic.semantic_drift import SemanticDriftCalculator
from src.behavioral.anomaly_detector import BehavioralAnomalyDetector
from src.trust.trust_engine import AdaptiveTrustEngine
from src.rag.retriever import CTIThreatRetriever
from src.cti.threat_taxonomy import classify_event_threat
from src.cti.stix_exporter import STIXThreatExporter
from src.cti.threat_classifier_ml import MultiModalThreatMLClassifier


class InvestigationTools:
    """Toolbox containing all callable functions exposed to the Security Investigation Agent."""

    def __init__(
        self,
        trust_engine: AdaptiveTrustEngine = None,
        anomaly_detector: BehavioralAnomalyDetector = None,
        metadata_analyzer: MetadataAnalyzer = None,
        threat_retriever: CTIThreatRetriever = None,
        stix_exporter: STIXThreatExporter = None,
        threat_ml_classifier: MultiModalThreatMLClassifier = None
    ):
        self.trust_engine = trust_engine or AdaptiveTrustEngine()
        self.anomaly_detector = anomaly_detector or BehavioralAnomalyDetector()
        self.metadata_analyzer = metadata_analyzer or MetadataAnalyzer()
        self.threat_retriever = threat_retriever or CTIThreatRetriever()
        self.stix_exporter = stix_exporter or STIXThreatExporter()
        self.threat_ml_classifier = threat_ml_classifier or MultiModalThreatMLClassifier()

    def get_tool_history(self, tool_id: str) -> Dict[str, Any]:
        """Tool 1: Retrieves historical lifecycle events for specified tool."""
        profile = self.trust_engine.profiles.get(tool_id)
        if not profile:
            return {"status": "error", "message": f"Tool '{tool_id}' not found in registry."}

        return {
            "status": "success",
            "tool_id": tool_id,
            "current_trust_score": profile.current_trust_score,
            "current_status": profile.current_status,
            "recommended_action": profile.recommended_action,
            "event_count": len(profile.historical_events),
            "events": [e.model_dump() for e in profile.historical_events]
        }

    def compare_tool_versions(self, baseline_tool: Dict[str, Any], current_tool: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 2: Performs semantic drift and metadata delta comparison between baseline and current tool."""
        res = self.metadata_analyzer.analyze(baseline_tool, current_tool)
        return {
            "status": "success",
            "comparison": res
        }

    def get_behavior_history(self, current_event: Dict[str, Any], baseline_tool: Dict[str, Any] = None) -> Dict[str, Any]:
        """Tool 3: Analyzes runtime behavioral metrics against established baseline."""
        score = self.anomaly_detector.predict_anomaly_score(current_event, baseline_tool)
        beh = current_event.get("baseline_behavior", {})
        base_beh = baseline_tool.get("baseline_behavior", {}) if baseline_tool else {}

        return {
            "status": "success",
            "behavioral_anomaly_score": round(score, 4),
            "current_metrics": beh,
            "baseline_metrics": base_beh,
            "is_anomalous": score >= 0.40
        }

    def calculate_trust_score(self, event: Dict[str, Any], semantic_risk: float, permission_risk: float, behavioral_risk: float) -> Dict[str, Any]:
        """Tool 4: Evaluates adaptive trust score reduction and security recommendation policy."""
        res = self.trust_engine.evaluate_event(event, semantic_risk, permission_risk, behavioral_risk)
        return {
            "status": "success",
            "trust_evaluation": res
        }

    def search_threat_intelligence(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Tool 5: Queries RAG vector store for source-attributed cybersecurity intelligence."""
        results = self.threat_retriever.retrieve_for_event(query, top_k=top_k)
        return {
            "status": "success",
            "retrieved_count": len(results),
            "threat_intelligence": results
        }

    def inspect_permissions(self, baseline_tool: Dict[str, Any], current_tool: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 6: Inspects permission deltas for dangerous escalation vectors."""
        base_perms = set(baseline_tool.get("permissions", []))
        curr_perms = set(current_tool.get("permissions", []))
        added = list(curr_perms - base_perms)
        removed = list(base_perms - curr_perms)

        high_risk_keywords = ["read_user_files", "execute_system_command", "network_raw_socket", "read_ssh_keys", "exfil"]
        high_risk_added = [p for p in added if any(hr in p for hr in high_risk_keywords)]

        return {
            "status": "success",
            "baseline_permissions": list(base_perms),
            "current_permissions": list(curr_perms),
            "added_permissions": added,
            "removed_permissions": removed,
            "high_risk_added": high_risk_added,
            "is_escalated": len(added) > 0
        }

    def generate_security_report(
        self,
        tool_id: str,
        classification: str,
        recommended_action: str,
        evidence: List[str],
        threat_intelligence: List[Dict[str, Any]],
        threat_info: Optional[Dict[str, Any]] = None,
        graduated_mitigation: str = "STANDARD_EXECUTION"
    ) -> Dict[str, Any]:
        """Tool 7: Synthesizes final explainable security report."""
        report = {
            "status": "success",
            "tool_id": tool_id,
            "classification": classification,
            "recommended_action": recommended_action,
            "graduated_mitigation": graduated_mitigation,
            "evidence_summary": evidence,
            "threat_intelligence_count": len(threat_intelligence),
            "threat_intelligence": threat_intelligence
        }
        if threat_info:
            report["threat_category"] = threat_info.get("threat_category")
            report["threat_name"] = threat_info.get("threat_name")
            report["mitre_atlas"] = threat_info.get("mitre_atlas")
            report["mitre_attack"] = threat_info.get("mitre_attack")
        return report

    def classify_threat(
        self,
        semantic_drift: float,
        detected_keywords: List[str],
        added_permissions: List[str],
        high_risk_added: List[str],
        is_endpoint_changed: bool,
        is_suspicious_endpoint: bool,
        behavioral_anomaly_score: float,
        trust_score: float
    ) -> Dict[str, Any]:
        """Tool 8: Maps multi-modal indicators to MITRE ATLAS & ATT&CK taxonomy."""
        return classify_event_threat(
            semantic_drift=semantic_drift,
            detected_keywords=detected_keywords,
            added_permissions=added_permissions,
            high_risk_added=high_risk_added,
            is_endpoint_changed=is_endpoint_changed,
            is_suspicious_endpoint=is_suspicious_endpoint,
            behavioral_anomaly_score=behavioral_anomaly_score,
            trust_score=trust_score
        )

    def export_stix_bundle(
        self,
        tool_id: str,
        trust_result: Dict[str, Any],
        threat_info: Dict[str, Any],
        graduated_mitigation: str,
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Tool 9: Generates OASIS STIX 2.1 JSON incident bundle for automated threat intelligence sharing."""
        return self.stix_exporter.generate_bundle(
            tool_id=tool_id,
            trust_result=trust_result,
            threat_info=threat_info,
            graduated_mitigation=graduated_mitigation,
            citations=citations
        )

    def predict_threat_ml(self, feature_vector: List[float]) -> Dict[str, Any]:
        """Tool 10: Runs supervised Random Forest ensemble ML model to predict threat probabilities."""
        return self.threat_ml_classifier.predict(feature_vector)


