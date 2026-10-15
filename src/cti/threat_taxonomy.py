"""
MITRE ATLAS & ATT&CK Threat Taxonomy Classifier for MCP-Based LLM Agents.
Maps multi-modal anomalies to standardized cybersecurity frameworks.
"""

from enum import Enum
from typing import Dict, Any, List, Optional


class ThreatCategory(str, Enum):
    TPA_METADATA_POISONING = "TPA_METADATA_POISONING"
    PERMISSION_ESCALATION = "PERMISSION_ESCALATION"
    C2_ENDPOINT_REDIRECTION = "C2_ENDPOINT_REDIRECTION"
    BEHAVIORAL_BURST_EXFILTRATION = "BEHAVIORAL_BURST_EXFILTRATION"
    COMBINED_RUG_PULL = "COMBINED_RUG_PULL"
    BENIGN_UPDATE = "BENIGN_UPDATE"


MITRE_ATLAS_TAXONOMY: Dict[str, Dict[str, Any]] = {
    ThreatCategory.TPA_METADATA_POISONING: {
        "primary_technique_id": "AML.T0054",
        "primary_technique_name": "LLM Tool Poisoning",
        "tactic": "Persistence / Execution",
        "url": "https://atlas.mitre.org/techniques/AML.T0054",
        "secondary_techniques": [
            {
                "technique_id": "AML.T0051",
                "technique_name": "LLM Indirect Prompt Injection",
                "url": "https://atlas.mitre.org/techniques/AML.T0051"
            }
        ],
        "cve_reference": "CWE-94: Improper Control of Generation of Code ('Code Injection')",
        "description": "Adversary alters MCP tool descriptions or schemas with covert directives to hijack host LLM agent reasoning."
    },
    ThreatCategory.PERMISSION_ESCALATION: {
        "primary_technique_id": "AML.T0043",
        "primary_technique_name": "AI Supply Chain Compromise / Capability Hijacking",
        "tactic": "Privilege Escalation",
        "url": "https://atlas.mitre.org/techniques/AML.T0043",
        "secondary_techniques": [
            {
                "technique_id": "AML.T0016",
                "technique_name": "Obtain Capabilities",
                "url": "https://atlas.mitre.org/techniques/AML.T0016"
            }
        ],
        "cve_reference": "CWE-250: Execution with Unnecessary Privileges",
        "description": "Compromised or adversarial MCP server requests dangerous capabilities (e.g. read_user_files, execute_system_command) unannounced post-approval."
    },
    ThreatCategory.C2_ENDPOINT_REDIRECTION: {
        "primary_technique_id": "AML.T0025",
        "primary_technique_name": "Exfiltration via Cyber Infrastructure",
        "tactic": "Command and Control / Exfiltration",
        "url": "https://atlas.mitre.org/techniques/AML.T0025",
        "secondary_techniques": [
            {
                "technique_id": "AML.T0015",
                "technique_name": "Evade ML Model",
                "url": "https://atlas.mitre.org/techniques/AML.T0015"
            }
        ],
        "cve_reference": "CWE-918: Server-Side Request Forgery (SSRF)",
        "description": "Outbound routing endpoints redirected to attacker-controlled C2 endpoints or unverified remote infrastructure."
    },
    ThreatCategory.BEHAVIORAL_BURST_EXFILTRATION: {
        "primary_technique_id": "AML.T0025",
        "primary_technique_name": "Exfiltration via Cyber Infrastructure",
        "tactic": "Exfiltration / Impact",
        "url": "https://atlas.mitre.org/techniques/AML.T0025",
        "secondary_techniques": [
            {
                "technique_id": "AML.T0029",
                "technique_name": "Denial of ML Service",
                "url": "https://atlas.mitre.org/techniques/AML.T0029"
            }
        ],
        "cve_reference": "CWE-770: Allocation of Resources Without Limits or Throttling",
        "description": "Anomalous call rate burst, failure rate variance, and excessive response payload sizes indicating automated data exfiltration."
    },
    ThreatCategory.COMBINED_RUG_PULL: {
        "primary_technique_id": "AML.T0054",
        "primary_technique_name": "Compound Multi-Vector MCP Rug-Pull Attack",
        "tactic": "Full Kill Chain (Initial Access to Exfiltration)",
        "url": "https://atlas.mitre.org/techniques/AML.T0054",
        "secondary_techniques": [
            {
                "technique_id": "AML.T0043",
                "technique_name": "AI Supply Chain Compromise",
                "url": "https://atlas.mitre.org/techniques/AML.T0043"
            },
            {
                "technique_id": "AML.T0025",
                "technique_name": "Exfiltration via Cyber Infrastructure",
                "url": "https://atlas.mitre.org/techniques/AML.T0025"
            }
        ],
        "cve_reference": "CWE-94 / CWE-250 / CWE-918",
        "description": "Coordinated multi-stage attack simultaneously mutating tool description, escalating privileges, redirecting endpoints, and exfiltrating data."
    },
    ThreatCategory.BENIGN_UPDATE: {
        "primary_technique_id": "NONE",
        "primary_technique_name": "Legitimate MCP Tool Maintenance",
        "tactic": "None (Safe Operation)",
        "url": "",
        "secondary_techniques": [],
        "cve_reference": "None",
        "description": "Normal schema optimization, documentation clarification, or bug fix within safe trust tolerances."
    }
}

MITRE_ATTACK_MAPPING: Dict[str, Dict[str, str]] = {
    ThreatCategory.TPA_METADATA_POISONING: {
        "attack_id": "T1059",
        "attack_name": "Command and Scripting Interpreter",
        "tactic": "Execution"
    },
    ThreatCategory.PERMISSION_ESCALATION: {
        "attack_id": "T1548",
        "attack_name": "Abuse Elevation Control Mechanism",
        "tactic": "Privilege Escalation"
    },
    ThreatCategory.C2_ENDPOINT_REDIRECTION: {
        "attack_id": "T1071",
        "attack_name": "Application Layer Protocol",
        "tactic": "Command and Control"
    },
    ThreatCategory.BEHAVIORAL_BURST_EXFILTRATION: {
        "attack_id": "T1041",
        "attack_name": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration"
    },
    ThreatCategory.COMBINED_RUG_PULL: {
        "attack_id": "T1195",
        "attack_name": "Supply Chain Compromise",
        "tactic": "Initial Access"
    },
    ThreatCategory.BENIGN_UPDATE: {
        "attack_id": "NONE",
        "attack_name": "Normal Operation",
        "tactic": "None"
    }
}


class ThreatTaxonomyClassifier:
    """Classifies detected multi-modal anomalies into standardized CTI threat categories."""

    @staticmethod
    def classify(
        semantic_drift: float,
        detected_keywords: List[str],
        added_permissions: List[str],
        high_risk_added: List[str],
        is_endpoint_changed: bool,
        is_suspicious_endpoint: bool,
        behavioral_anomaly_score: float,
        trust_score: float
    ) -> Dict[str, Any]:
        """Classifies observed changes into an exact threat vector and maps to MITRE ATLAS/ATT&CK."""
        detected_vectors = []

        is_meta_threat = (len(detected_keywords) > 0) or (semantic_drift >= 0.25)
        is_perm_threat = (len(high_risk_added) > 0) or (len(added_permissions) >= 2)
        is_endp_threat = is_suspicious_endpoint or (is_endpoint_changed and semantic_drift > 0.15)
        is_beh_threat = behavioral_anomaly_score >= 0.40

        if is_meta_threat:
            detected_vectors.append("METADATA_INJECTION")
        if is_perm_threat:
            detected_vectors.append("PRIVILEGE_ESCALATION")
        if is_endp_threat:
            detected_vectors.append("ENDPOINT_DRIFT")
        if is_beh_threat:
            detected_vectors.append("BEHAVIORAL_BURST")

        # Determine Primary Category
        threat_count = sum([is_meta_threat, is_perm_threat, is_endp_threat, is_beh_threat])

        if threat_count >= 2:
            primary_category = ThreatCategory.COMBINED_RUG_PULL
        elif is_meta_threat:
            primary_category = ThreatCategory.TPA_METADATA_POISONING
        elif is_perm_threat:
            primary_category = ThreatCategory.PERMISSION_ESCALATION
        elif is_endp_threat:
            primary_category = ThreatCategory.C2_ENDPOINT_REDIRECTION
        elif is_beh_threat:
            primary_category = ThreatCategory.BEHAVIORAL_BURST_EXFILTRATION
        else:
            primary_category = ThreatCategory.BENIGN_UPDATE

        # Calculate Severity Level
        if trust_score < 50.0:
            severity = "CRITICAL"
        elif trust_score < 65.0:
            severity = "HIGH"
        elif trust_score < 80.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        atlas_info = MITRE_ATLAS_TAXONOMY.get(primary_category, MITRE_ATLAS_TAXONOMY[ThreatCategory.BENIGN_UPDATE])
        attack_info = MITRE_ATTACK_MAPPING.get(primary_category, MITRE_ATTACK_MAPPING[ThreatCategory.BENIGN_UPDATE])

        return {
            "threat_category": primary_category.value,
            "threat_name": atlas_info["primary_technique_name"],
            "severity": severity,
            "detected_vectors": detected_vectors,
            "mitre_atlas": {
                "technique_id": atlas_info["primary_technique_id"],
                "technique_name": atlas_info["primary_technique_name"],
                "tactic": atlas_info["tactic"],
                "url": atlas_info["url"],
                "secondary_techniques": atlas_info["secondary_techniques"],
                "cve_reference": atlas_info["cve_reference"]
            },
            "mitre_attack": {
                "technique_id": attack_info["attack_id"],
                "technique_name": attack_info["attack_name"],
                "tactic": attack_info["tactic"]
            },
            "threat_description": atlas_info["description"]
        }


def classify_event_threat(
    semantic_drift: float,
    detected_keywords: List[str],
    added_permissions: List[str],
    high_risk_added: List[str],
    is_endpoint_changed: bool,
    is_suspicious_endpoint: bool,
    behavioral_anomaly_score: float,
    trust_score: float
) -> Dict[str, Any]:
    """Helper wrapper for threat taxonomy classification."""
    return ThreatTaxonomyClassifier.classify(
        semantic_drift=semantic_drift,
        detected_keywords=detected_keywords,
        added_permissions=added_permissions,
        high_risk_added=high_risk_added,
        is_endpoint_changed=is_endpoint_changed,
        is_suspicious_endpoint=is_suspicious_endpoint,
        behavioral_anomaly_score=behavioral_anomaly_score,
        trust_score=trust_score
    )
