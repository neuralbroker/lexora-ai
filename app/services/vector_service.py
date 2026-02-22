"""Vector storage service using FAISS."""

import json
import os
from pathlib import Path
from typing import Optional

import faiss
import numpy as np

from app.config import get_settings
from app.core.logging import get_logger
from app.services.embedding_service import get_embedding_service

settings = get_settings()
logger = get_logger(__name__)


class VectorStore:
    """
    FAISS-based vector store for document embeddings.
    
    Features:
    - Persistent storage with JSON metadata
    - User-level isolation
    - Efficient similarity search
    - Incremental updates
    
    Design decision: Use FAISS for its speed and recall performance.
    For 10k+ users, consider migrating to Pinecone or Weaviate.
    """

    def __init__(self, user_id: str, dimension: int = 1536):
        """
        Initialize vector store for a user.
        
        Args:
            user_id: User ID for isolation
            dimension: Embedding dimension
        """
        self.user_id = user_id
        self.dimension = dimension
        self.index_path = self._get_index_path()
        self.metadata_path = self._get_metadata_path()
        self.index: Optional[faiss.Index] = None
        self.metadata: list[dict] = []
        self._load_or_create_index()

    def _get_index_path(self) -> str:
        """Get path for FAISS index file."""
        base_path = Path(settings.faiss_index_path) / self.user_id
        base_path.mkdir(parents=True, exist_ok=True)
        return str(base_path / "index.faiss")

    def _get_metadata_path(self) -> str:
        """Get path for metadata JSON file."""
        base_path = Path(settings.faiss_index_path) / self.user_id
        base_path.mkdir(parents=True, exist_ok=True)
        return str(base_path / "metadata.json")

    def _load_or_create_index(self) -> None:
        """Load existing index or create new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
                logger.info("index_loaded", user_id=self.user_id, vectors=len(self.metadata))
            except Exception as e:
                logger.warning(
                    "index_load_failed",
                    user_id=self.user_id,
                    error=str(e),
                )
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info("index_created", user_id=self.user_id, dimension=self.dimension)

    def add_vectors(
        self,
        vectors: list[list[float]],
        documents: list[str],
        document_ids: list[str],
    ) -> list[str]:
        """
        Add vectors to the index.
        
        Args:
            vectors: List of embedding vectors
            documents: List of text chunks
            document_ids: List of source document IDs
        
        Returns:
            List of vector IDs
        """
        if not vectors:
            return []

        vectors_array = np.array(vectors, dtype=np.float32)
        
        if vectors_array.ndim == 1:
            vectors_array = vectors_array.reshape(1, -1)

        vector_ids = []
        start_id = len(self.metadata)

        for i, (vector, doc, doc_id) in enumerate(zip(vectors, documents, document_ids)):
            vector_ids.append(f"vec_{start_id + i}")
            self.metadata.append({
                "id": f"vec_{start_id + i}",
                "text": doc,
                "document_id": doc_id,
            })

        self.index.add(vectors_array)
        self._save()

        logger.info(
            "vectors_added",
            user_id=self.user_id,
            count=len(vectors),
            total=self.index.ntotal,
        )

        return vector_ids

    def search(
        self,
        query_vector: list[float],
        k: int = 4,
        document_ids: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding
            k: Number of results to return
            document_ids: Optional filter by document IDs
        
        Returns:
            List of matching documents with scores
        """
        if self.index.ntotal == 0:
            return []

        query_array = np.array([query_vector], dtype=np.float32)
        
        if self.index.ntotal < k:
            k = self.index.ntotal

        distances, indices = self.index.search(query_array, k)

        results = []
        seen = set()

        for distance, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]
            
            if document_ids and meta["document_id"] not in document_ids:
                continue

            if meta["id"] in seen:
                continue

            seen.add(meta["id"])
            results.append({
                "text": meta["text"],
                "document_id": meta["document_id"],
                "vector_id": meta["id"],
                "score": float(distance),
            })

        return results

    def delete_vectors(self, document_id: str) -> bool:
        """
        Delete all vectors associated with a document.
        
        Note: FAISS doesn't support direct deletion, so we rebuild.
        For production with frequent deletions, consider using
        a different index type or database.
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            True if successful
        """
        original_count = len(self.metadata)
        self.metadata = [m for m in self.metadata if m["document_id"] != document_id]

        if len(self.metadata) == original_count:
            return False

        self._rebuild_index()
        logger.info("vectors_deleted", user_id=self.user_id, document_id=document_id)
        return True

    def _rebuild_index(self) -> None:
        """Rebuild FAISS index from metadata."""
        if not self.metadata:
            self.index = faiss.IndexFlatL2(self.dimension)
            self._save()
            return

        texts = [m["text"] for m in self.metadata]
        embedding_service = get_embedding_service()
        vectors = embedding_service.embed_documents(texts)

        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(vectors, dtype=np.float32))
        self._save()

    def _save(self) -> None:
        """Save index and metadata to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
        
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f)

    def get_stats(self) -> dict:
        """Get vector store statistics."""
        return {
            "user_id": self.user_id,
            "total_vectors": self.index.ntotal if self.index else 0,
            "documents": len(set(m["document_id"] for m in self.metadata)),
        }


class VectorStoreManager:
    """
    Manager for multiple user vector stores.
    
    Provides caching and lifecycle management.
    """

    def __init__(self):
        self._stores: dict[str, VectorStore] = {}

    def get_store(self, user_id: str, dimension: int = 1536) -> VectorStore:
        """
        Get or create vector store for a user.
        
        Args:
            user_id: User ID
            dimension: Embedding dimension
        
        Returns:
            VectorStore instance
        """
        if user_id not in self._stores:
            self._stores[user_id] = VectorStore(user_id, dimension)
        
        return self._stores[user_id]

    def delete_store(self, user_id: str) -> bool:
        """Delete user's vector store."""
        if user_id in self._stores:
            del self._stores[user_id]
            return True
        return False


vector_store_manager = VectorStoreManager()


def get_vector_store(user_id: str) -> VectorStore:
    """Factory function to get vector store."""
    return vector_store_manager.get_store(user_id)
