"""
Unit tests for semantic embeddings, drift calculation, and metadata analysis.
"""

import pytest
from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.data.rugpull_generator import RugPullDatasetGenerator
from src.semantic import EmbeddingEngine, SemanticDriftCalculator, MetadataAnalyzer


def test_embedding_engine():
    engine = EmbeddingEngine()
    emb = engine.encode(["Search weather", "Weather lookup query"])
    assert emb.shape[0] == 2
    sim = engine.compute_similarity("Search weather", "Search weather forecast")
    assert 0.0 <= sim <= 1.0
    assert sim > 0.5


def test_semantic_drift_calculator():
    calc = SemanticDriftCalculator()
    t1 = AUTHENTIC_MCP_TOOLS[0]
    gen = RugPullDatasetGenerator()
    base, attack = gen.generate_metadata_rugpull(t1)

    drift_res = calc.calculate_drift(base, attack)
    assert "semantic_drift" in drift_res
    assert drift_res["semantic_drift"] > 0.15
    assert drift_res["is_description_changed"] is True


def test_metadata_analyzer():
    analyzer = MetadataAnalyzer()
    t1 = AUTHENTIC_MCP_TOOLS[0]
    gen = RugPullDatasetGenerator()

    base, meta_attack = gen.generate_metadata_rugpull(t1)
    res = analyzer.analyze(base, meta_attack)
    assert len(res["detected_keywords"]) > 0
    assert res["metadata_risk_score"] > 0.20

    base, perm_attack = gen.generate_permission_rugpull(t1)
    res_p = analyzer.analyze(base, perm_attack)
    assert len(res_p["high_risk_added_permissions"]) > 0
