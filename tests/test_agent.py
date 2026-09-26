"""
Unit tests for Security Investigation Agent tools and workflow.
"""

import pytest
from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.data.rugpull_generator import RugPullDatasetGenerator
from src.agent import InvestigationTools, SecurityInvestigationAgent, SecurityWorkflowGraph


def test_investigation_tools():
    tools = InvestigationTools()
    tool = AUTHENTIC_MCP_TOOLS[0]
    gen = RugPullDatasetGenerator()
    base, attack = gen.generate_metadata_rugpull(tool)

    cmp_res = tools.compare_tool_versions(base, attack)
    assert cmp_res["status"] == "success"

    perm_res = tools.inspect_permissions(base, attack)
    assert perm_res["status"] == "success"

    beh_res = tools.get_behavior_history(attack, base)
    assert beh_res["status"] == "success"

    rag_res = tools.search_threat_intelligence("Rug pull attack")
    assert rag_res["status"] == "success"


def test_security_agent_investigation():
    agent = SecurityInvestigationAgent()
    tool = AUTHENTIC_MCP_TOOLS[0]
    gen = RugPullDatasetGenerator()
    base, attack = gen.generate_metadata_rugpull(tool)

    res = agent.investigate(base, attack)
    assert "tool_id" in res
    assert "current_trust_score" in res
    assert "classification" in res
    assert "recommended_action" in res
    assert "threat_intelligence" in res
    assert len(res["invoked_tools"]) >= 5


def test_workflow_graph():
    graph = SecurityWorkflowGraph()
    tool = AUTHENTIC_MCP_TOOLS[0]
    gen = RugPullDatasetGenerator()
    base, attack = gen.generate_metadata_rugpull(tool)

    res = graph.run(base, attack)
    assert res["classification"] in ["SAFE", "SUSPICIOUS", "RUG_PULL"]
