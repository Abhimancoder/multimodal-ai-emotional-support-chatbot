import math
import re
import hashlib
from pathlib import Path
from typing import List
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb import EmbeddingFunction, Documents, Embeddings
from backend.core.config import settings, BASE_DIR
from backend.core.logging import logger

STOPWORDS = {
    "the", "a", "an", "is", "it", "to", "of", "and", "or", "in", "on", "at",
    "by", "for", "with", "about", "how", "do", "does", "i", "you", "my", "your",
    "this", "that", "can", "could", "should", "what", "tell", "me", "please"
}

class LocalOfflineEmbeddingFunction(EmbeddingFunction):
    """
    Fast, deterministic, 100% offline semantic vector embedding function.
    Transforms text into normalized 384-dimensional dense vectors using
    content-word filtering and bigram feature hashing.
    Requires ZERO network access, ZERO external model downloads, and zero API costs.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def name(self) -> str:
        return "local_offline_feature_hasher"

    def get_config(self) -> dict:
        return {"dimension": self.dimension}

    def __call__(self, input: Documents) -> Embeddings:
        embeddings: Embeddings = []
        for text in input:
            vec = [0.0] * self.dimension
            # Extract content words ignoring common stopwords
            words = [w for w in re.findall(r"\w+", text.lower()) if w not in STOPWORDS]

            # 1. Unigram features
            for w in words:
                idx = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % self.dimension
                vec[idx] += 2.0

            # 2. Bigram features for phrase semantics
            for i in range(len(words) - 1):
                bi = f"{words[i]}_{words[i+1]}"
                idx = int(hashlib.md5(bi.encode("utf-8")).hexdigest(), 16) % self.dimension
                vec[idx] += 3.0

            # L2 Normalization to unit sphere for accurate cosine similarity
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]

            embeddings.append(vec)
        return embeddings

class VectorStore:
    """
    Manages persistent local ChromaDB instance for semantic search.
    Runs 100% locally with zero external API calls or subscription costs.
    """

    def __init__(self):
        self.persist_dir = BASE_DIR / settings.CHROMA_PERSIST_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_fn = LocalOfflineEmbeddingFunction(dimension=384)

        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection with cosine space
        self.collection = self.client.get_or_create_collection(
            name="mindful_knowledge_base",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine", "description": "Curated psychoeducation and coping techniques"}
        )
        logger.info(f"ChromaDB initialized at: {self.persist_dir} (Collection count: {self.collection.count()})")

    def add_chunks(self, ids: list, documents: list, metadatas: list) -> None:
        """Upserts text chunks into the vector store with deterministic IDs."""
        if not ids:
            return
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Upserted {len(ids)} chunks into ChromaDB.")

    def query(self, query_text: str, n_results: int = 3) -> dict:
        """Executes semantic similarity search against the indexed collection."""
        if self.collection.count() == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        return self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, self.collection.count())
        )

vector_store = VectorStore()
