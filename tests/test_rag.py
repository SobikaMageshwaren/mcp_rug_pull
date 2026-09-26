"""
Unit tests for RAG threat intelligence vector store and retriever.
"""

import pytest
from src.rag import CTI_KNOWLEDGE_CORPUS, FAISSVectorStore, CTIThreatRetriever


def test_cti_knowledge_corpus():
    assert len(CTI_KNOWLEDGE_CORPUS) >= 5
    for doc in CTI_KNOWLEDGE_CORPUS:
        assert "doc_id" in doc
        assert "title" in doc
        assert "source" in doc
        assert "url" in doc
        assert "content" in doc


def test_faiss_vector_store():
    store = FAISSVectorStore()
    store.build_index(CTI_KNOWLEDGE_CORPUS)
    results = store.search("Tool Poisoning Attacks in MCP", top_k=2)
    assert len(results) == 2
    top_doc, score = results[0]
    assert "title" in top_doc
    assert "content" in top_doc
    assert score > 0.0


def test_cti_threat_retriever():
    retriever = CTIThreatRetriever()
    results = retriever.retrieve_for_event("Unannounced permission escalation and endpoint drift")
    assert len(results) > 0
    assert "source" in results[0]
    assert "url" in results[0]
