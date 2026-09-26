"""
Semantic Drift Calculator.
Measures semantic drift, embedding similarity, and structural changes between tool versions.
"""

import json
from typing import Dict, Any
from src.semantic.embeddings import EmbeddingEngine


class SemanticDriftCalculator:
    """Calculates semantic drift and embedding shift across tool versions."""

    def __init__(self, embedding_engine: EmbeddingEngine = None):
        self.engine = embedding_engine or EmbeddingEngine()

    def calculate_drift(self, baseline_tool: Dict[str, Any], current_tool: Dict[str, Any]) -> Dict[str, Any]:
        """Compares baseline tool definition with current version to measure semantic drift."""
        base_desc = baseline_tool.get("description", "")
        curr_desc = current_tool.get("description", "")

        # Compute embedding similarity on descriptions
        similarity = self.engine.compute_similarity(base_desc, curr_desc)
        drift = max(0.0, min(1.0, 1.0 - similarity))

        # Check full schema change
        base_schema_str = json.dumps(baseline_tool.get("input_schema", {}), sort_keys=True)
        curr_schema_str = json.dumps(current_tool.get("input_schema", {}), sort_keys=True)
        schema_similarity = self.engine.compute_similarity(base_schema_str, curr_schema_str)
        schema_drift = max(0.0, min(1.0, 1.0 - schema_similarity))

        # Combined drift
        combined_drift = 0.7 * drift + 0.3 * schema_drift

        return {
            "embedding_similarity": round(similarity, 4),
            "semantic_drift": round(combined_drift, 4),
            "description_drift": round(drift, 4),
            "schema_drift": round(schema_drift, 4),
            "is_description_changed": base_desc != curr_desc,
            "is_schema_changed": base_schema_str != curr_schema_str
        }
