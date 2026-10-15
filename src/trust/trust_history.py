"""
Trust Profile and History Models.
Pydantic and dataclass models tracking tool lifecycle, fingerprints, and historical events.
"""

import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HistoricalEvent(BaseModel):
    """Record of a past evaluation event for a tool."""
    timestamp: float = Field(default_factory=time.time)
    version: str
    change_type: str
    semantic_drift: float
    behavioral_anomaly_score: float
    permission_risk: float
    trust_score_after: float
    classification: str
    recommended_action: str
    graduated_mitigation: str = "STANDARD_EXECUTION"


class TrustProfile(BaseModel):
    """Complete trust profile maintained per MCP tool."""
    tool_id: str
    server_id: str
    initial_trust_score: float = 100.0
    current_trust_score: float = 100.0
    metadata_fingerprint: str = ""
    semantic_fingerprint: List[float] = Field(default_factory=list)
    permission_profile: List[str] = Field(default_factory=list)
    behavioral_baseline: Dict[str, Any] = Field(default_factory=dict)
    historical_events: List[HistoricalEvent] = Field(default_factory=list)
    risk_history: List[float] = Field(default_factory=list)
    last_verified_timestamp: float = Field(default_factory=time.time)
    current_status: str = "SAFE"  # SAFE, SUSPICIOUS, RUG-PULL
    recommended_action: str = "ALLOW"  # ALLOW, MONITOR, REQUIRE HUMAN APPROVAL, BLOCK
    graduated_mitigation: str = "STANDARD_EXECUTION"
