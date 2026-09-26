"""
RAG Knowledge Base Ingestion Script.
Indexes CTI threat corpus into FAISS vector store and saves to disk.
"""

import os
import json
from src.rag.knowledge_base import CTI_KNOWLEDGE_CORPUS
from src.rag.vector_store import FAISSVectorStore


def run_ingestion(output_path: str = "data/processed/threat_intel_kb.json") -> FAISSVectorStore:
    """Ingests threat intelligence corpus and saves vector index."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"[RAG Ingestion] Indexing {len(CTI_KNOWLEDGE_CORPUS)} Threat Intelligence documents...")
    vector_store = FAISSVectorStore()
    vector_store.build_index(CTI_KNOWLEDGE_CORPUS)
    vector_store.save(output_path)

    print(f"[RAG Ingestion] Index successfully saved to {output_path}")
    return vector_store


if __name__ == "__main__":
    run_ingestion()
