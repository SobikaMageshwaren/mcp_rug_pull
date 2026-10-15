"""
Cyber Threat Intelligence (CTI) Module.
Provides MITRE ATLAS / ATT&CK threat taxonomy classification and STIX 2.1 bundle generation.
"""

from src.cti.threat_taxonomy import (
    ThreatTaxonomyClassifier,
    ThreatCategory,
    classify_event_threat
)
from src.cti.stix_exporter import STIXThreatExporter
from src.cti.threat_classifier_ml import MultiModalThreatMLClassifier

__all__ = [
    "ThreatTaxonomyClassifier",
    "ThreatCategory",
    "classify_event_threat",
    "STIXThreatExporter",
    "MultiModalThreatMLClassifier"
]
