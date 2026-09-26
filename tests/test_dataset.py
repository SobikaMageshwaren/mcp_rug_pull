"""
Unit tests for dataset generation and baseline MCP tools.
"""

import pytest
from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.data.rugpull_generator import RugPullDatasetGenerator


def test_authentic_mcp_tools_schema():
    assert len(AUTHENTIC_MCP_TOOLS) >= 10
    for tool in AUTHENTIC_MCP_TOOLS:
        assert "tool_id" in tool
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert "permissions" in tool
        assert "endpoint" in tool
        assert "baseline_behavior" in tool


def test_rugpull_generator_scenarios():
    gen = RugPullDatasetGenerator(random_seed=42)
    tool = AUTHENTIC_MCP_TOOLS[0]

    trusted, meta_attack = gen.generate_metadata_rugpull(tool)
    assert meta_attack["change_type"] == "METADATA_RUG_PULL"
    assert meta_attack["label"] == "RUG_PULL"
    assert "exfil" in meta_attack["description"].lower() or "secrets" in meta_attack["description"].lower()

    _, perm_attack = gen.generate_permission_rugpull(tool)
    assert perm_attack["change_type"] == "PERMISSION_RUG_PULL"
    assert len(perm_attack["permissions"]) > len(trusted["permissions"])

    _, end_attack = gen.generate_endpoint_rugpull(tool)
    assert end_attack["change_type"] == "ENDPOINT_RUG_PULL"
    assert "unknown-external" in end_attack["endpoint"]

    _, beh_attack = gen.generate_behavioral_rugpull(tool)
    assert beh_attack["change_type"] == "BEHAVIORAL_RUG_PULL"
    assert beh_attack["baseline_behavior"]["calls_per_minute"] > trusted["baseline_behavior"]["calls_per_minute"]

    _, comb_attack = gen.generate_combined_rugpull(tool)
    assert comb_attack["change_type"] == "COMBINED_RUG_PULL"


def test_full_dataset_generation():
    gen = RugPullDatasetGenerator(random_seed=42)
    events = gen.build_full_dataset()
    assert len(events) == 40
    benign_count = sum(1 for e in events if e["label"] == "BENIGN")
    attack_count = sum(1 for e in events if e["label"] == "RUG_PULL")
    assert benign_count == 30
    assert attack_count == 10
