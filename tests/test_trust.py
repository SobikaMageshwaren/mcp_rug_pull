"""
Unit tests for adaptive trust profile and score calculation.
"""

import pytest
from src.trust import AdaptiveTrustEngine, TrustProfile


def test_trust_engine_registration():
    engine = AdaptiveTrustEngine()
    profile = engine.register_tool({"tool_id": "test_01", "server_id": "server_01"})
    assert profile.tool_id == "test_01"
    assert profile.current_trust_score == 100.0
    assert profile.current_status == "SAFE"


def test_trust_score_reduction_and_classification():
    engine = AdaptiveTrustEngine()
    engine.register_tool({"tool_id": "test_01", "server_id": "server_01"})

    # Benign event -> score remains high
    res_benign = engine.evaluate_event({"tool_id": "test_01"}, semantic_risk=0.0, permission_risk=0.0, behavioral_anomaly_score=0.0)
    assert res_benign["current_trust_score"] >= 80.0
    assert res_benign["classification"] == "SAFE"
    assert res_benign["recommended_action"] == "ALLOW"

    # Severe attack event -> score drops significantly
    res_attack = engine.evaluate_event({"tool_id": "test_01"}, semantic_risk=0.9, permission_risk=0.9, behavioral_anomaly_score=0.9)
    assert res_attack["current_trust_score"] < 50.0
    assert res_attack["classification"] == "RUG_PULL"
    assert res_attack["recommended_action"] == "BLOCK"
