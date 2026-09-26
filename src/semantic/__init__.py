"""
Semantic Analysis Package.
Includes Transformer embeddings, semantic drift computation, and MCP metadata analysis.
"""

from src.semantic.embeddings import EmbeddingEngine
from src.semantic.semantic_drift import SemanticDriftCalculator
from src.semantic.metadata_analyzer import MetadataAnalyzer

__all__ = ["EmbeddingEngine", "SemanticDriftCalculator", "MetadataAnalyzer"]
