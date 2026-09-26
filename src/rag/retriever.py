"""
CTI Threat Intelligence Retriever.
Queries the vector store for security evidence relevant to detected tool events.
Ensures source attribution and traceable citations.
"""

import os
from typing import List, Dict, Any
from src.rag.vector_store import FAISSVectorStore
from src.rag.knowledge_base import CTI_KNOWLEDGE_CORPUS


class CTIThreatRetriever:
    """Retrieves context-relevant threat intelligence documents with source attribution."""

    def __init__(self, kb_path: str = "data/processed/threat_intel_kb.json"):
        self.vector_store = FAISSVectorStore()
        if os.path.exists(kb_path):
            try:
                self.vector_store.load(kb_path)
            except Exception as e:
                print(f"[CTIThreatRetriever] Warning: Loading index failed ({e}). Building in-memory.")
                self.vector_store.build_index(CTI_KNOWLEDGE_CORPUS)
        else:
            self.vector_store.build_index(CTI_KNOWLEDGE_CORPUS)

    def retrieve_for_event(self, event_summary: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant threat intelligence passages with full metadata."""
        matches = self.vector_store.search(event_summary, top_k=top_k)

        results = []
        for doc, score in matches:
            results.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "source": doc["source"],
                "url": doc["url"],
                "publication_date": doc["publication_date"],
                "attack_category": doc["attack_category"],
                "snippet": doc["content"],
                "relevance_score": round(score, 4)
            })
        return results


if __name__ == "__main__":
    retriever = CTIThreatRetriever()
    results = retriever.retrieve_for_event("Tool description changed to exfiltrate user environment keys to external service")
    import json
    print("Retrieved Threat Intelligence:")
    print(json.dumps(results, indent=2))
