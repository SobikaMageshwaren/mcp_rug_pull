"""
End-to-End Integration Tests.
Verifies pipeline execution across Benign Updates and all 5 Controlled Rug-Pull Scenarios.
"""

import pytest
from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.data.rugpull_generator import RugPullDatasetGenerator
from src.agent import SecurityInvestigationAgent


@pytest.fixture
def agent_fixture():
    return SecurityInvestigationAgent()


@pytest.fixture
def generator_fixture():
    return RugPullDatasetGenerator(random_seed=42)


def test_scenario_0_benign_update(agent_fixture, generator_fixture):
    tool = AUTHENTIC_MCP_TOOLS[0]
    base, benign_update = generator_fixture.generate_legitimate_update(tool)

    res = agent_fixture.investigate(base, benign_update)
    assert res["classification"] == "SAFE"
    assert res["recommended_action"] == "ALLOW"
    assert res["current_trust_score"] >= 80.0


def test_scenario_1_metadata_rugpull(agent_fixture, generator_fixture):
    tool = AUTHENTIC_MCP_TOOLS[0]
    base, attack = generator_fixture.generate_metadata_rugpull(tool)

    res = agent_fixture.investigate(base, attack)
    assert "description changed" in " ".join(res["evidence"]).lower() or "suspicious" in " ".join(res["evidence"]).lower()


def test_scenario_2_permission_rugpull(agent_fixture, generator_fixture):
    tool = AUTHENTIC_MCP_TOOLS[1]
    base, attack = generator_fixture.generate_permission_rugpull(tool)

    res = agent_fixture.investigate(base, attack)
    assert res["permission_risk"] > 0.0
    assert "added permissions" in " ".join(res["evidence"]).lower() or "privilege" in " ".join(res["evidence"]).lower()


def test_scenario_3_endpoint_rugpull(agent_fixture, generator_fixture):
    tool = AUTHENTIC_MCP_TOOLS[2]
    base, attack = generator_fixture.generate_endpoint_rugpull(tool)

    res = agent_fixture.investigate(base, attack)
    assert "endpoint" in " ".join(res["evidence"]).lower() or "suspicious domain" in " ".join(res["evidence"]).lower()


def test_scenario_4_behavioral_rugpull(agent_fixture, generator_fixture):
    tool = AUTHENTIC_MCP_TOOLS[3]
    base, attack = generator_fixture.generate_behavioral_rugpull(tool)

    res = agent_fixture.investigate(base, attack)
    assert res["behavioral_anomaly_score"] > 0.20


def test_scenario_5_combined_rugpull(agent_fixture, generator_fixture):
    tool = AUTHENTIC_MCP_TOOLS[4]
    base, attack = generator_fixture.generate_combined_rugpull(tool)

    res = agent_fixture.investigate(base, attack)
    assert res["classification"] in ["SUSPICIOUS", "RUG_PULL"]
    assert res["recommended_action"] in ["MONITOR", "REQUIRE HUMAN APPROVAL", "BLOCK"]
    assert len(res["evidence"]) >= 2
