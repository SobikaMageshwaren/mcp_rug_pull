"""
Transformer Embedding Engine for MCP Tool Metadata.
Uses SentenceTransformers (all-MiniLM-L6-v2) for semantic embedding generation.
Includes robust fallback for offline or restricted execution environments.
"""

import numpy as np
from typing import List, Union


class EmbeddingEngine:
    """Generates vector embeddings for MCP tool metadata and descriptions."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Attempts to load sentence-transformers model; falls back to TF-IDF if offline."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.use_fallback = False
        except Exception as e:
            print(f"[EmbeddingEngine] Warning: SentenceTransformer load failed ({e}). Using lightweight vectorizer fallback.")
            self.use_fallback = True
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.fallback_vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encodes text or list of texts into embedding vectors."""
        if isinstance(texts, str):
            texts = [texts]

        if not self.use_fallback and self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        else:
            # Fallback TF-IDF encoding normalized to unit norm
            try:
                matrix = self.fallback_vectorizer.fit_transform(texts).toarray()
                norms = np.linalg.norm(matrix, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                return matrix / norms
            except Exception:
                # Basic dummy vector if corpus too small for tfidf
                arr = np.zeros((len(texts), 384))
                for i, text in enumerate(texts):
                    for char in text:
                        arr[i, ord(char) % 384] += 1.0
                    norm = np.linalg.norm(arr[i])
                    if norm > 0:
                        arr[i] /= norm
                return arr

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Calculates cosine similarity between two text snippets [0.0, 1.0]."""
        emb = self.encode([text1, text2])
        vec1, vec2 = emb[0], emb[1]
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        similarity = float(np.dot(vec1, vec2) / (norm1 * norm2))
        return max(0.0, min(1.0, similarity))
