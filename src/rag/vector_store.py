"""
FAISS Vector Store for Threat Intelligence.
Indexes document chunks with SentenceTransformer embeddings and supports similarity searches.
"""

import json
import os
import numpy as np
from typing import List, Dict, Any, Tuple
from src.semantic.embeddings import EmbeddingEngine


class FAISSVectorStore:
    """Vector database index using FAISS (or numpy cosine similarity index)."""

    def __init__(self, embedding_engine: EmbeddingEngine = None):
        self.engine = embedding_engine or EmbeddingEngine()
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.faiss_index = None

    def build_index(self, documents: List[Dict[str, Any]]):
        """Indexes documents and generates embeddings."""
        self.documents = documents
        texts = [doc["content"] for doc in documents]

        # Generate embeddings
        embs = self.engine.encode(texts)
        self.embeddings = embs.astype(np.float32)

        try:
            import faiss
            dim = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dim)  # Inner product on normalized vectors = Cosine similarity
            # Normalize embeddings for cosine similarity
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            norm_embs = self.embeddings / norms
            self.faiss_index.add(norm_embs)
            self.use_faiss = True
        except Exception as e:
            print(f"[FAISSVectorStore] Warning: FAISS index creation failed ({e}). Using Numpy cosine fallback.")
            self.use_faiss = False

    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """Performs semantic similarity search returning top-k matching documents and scores."""
        if not self.documents:
            return []

        q_emb = self.engine.encode([query]).astype(np.float32)
        q_norm = np.linalg.norm(q_emb)
        if q_norm > 0:
            q_emb /= q_norm

        if getattr(self, "use_faiss", False) and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(q_emb, min(top_k, len(self.documents)))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    results.append((self.documents[idx], float(score)))
            return results
        else:
            # Numpy fallback
            norms = np.linalg.norm(self.embeddings, axis=1)
            norms[norms == 0] = 1.0
            sims = np.dot(self.embeddings, q_emb.T).flatten() / norms
            top_indices = np.argsort(sims)[::-1][:top_k]
            results = []
            for idx in top_indices:
                results.append((self.documents[idx], float(sims[idx])))
            return results

    def save(self, filepath: str):
        """Saves index metadata to disk."""
        data = {
            "documents": self.documents,
            "embeddings": self.embeddings.tolist() if self.embeddings is not None else []
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str):
        """Loads index metadata from disk."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.documents = data["documents"]
        self.embeddings = np.array(data["embeddings"], dtype=np.float32)
        self.build_index(self.documents)
