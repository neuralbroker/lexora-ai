"""Retrieval service for finding relevant documents."""

from typing import Optional

from app.config import get_settings
from app.core.logging import get_logger
from app.services.embedding_service import get_embedding_service
from app.services.vector_service import get_vector_store

settings = get_settings()
logger = get_logger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant documents using similarity search.
    
    Features:
    - Semantic search using embeddings
    - Configurable result count
    - Document filtering
    - Source tracking
    
    Design decision: Simple retrieval-first approach.
    For production, consider adding:
    - Re-ranking (e.g., Cohere reranker)
    - Hybrid search (BM25 + vector)
    - Query expansion
    """

    def __init__(
        self,
        user_id: str,
        embedding_service=None,
        vector_store=None,
    ):
        """
        Initialize retrieval service.
        
        Args:
            user_id: User ID for vector store access
            embedding_service: Optional embedding service
            vector_store: Optional vector store
        """
        self.user_id = user_id
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or get_vector_store(user_id)

    def retrieve(
        self,
        query: str,
        k: int = 4,
        document_ids: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query string
            k: Number of results to return
            document_ids: Optional filter by document IDs
        
        Returns:
            List of relevant document chunks with metadata
        """
        logger.info("retrieval_started", user_id=self.user_id, query=query[:100])

        query_embedding = self.embedding_service.embed_query(query)

        results = self.vector_store.search(
            query_vector=query_embedding,
            k=k * 2,  # Get more results for filtering
            document_ids=document_ids,
        )

        filtered_results = self._filter_and_rank(results, k)

        logger.info(
            "retrieval_completed",
            user_id=self.user_id,
            results_found=len(filtered_results),
        )

        return filtered_results

    def _filter_and_rank(self, results: list[dict], k: int) -> list[dict]:
        """
        Filter and rank retrieval results.
        
        Args:
            results: Raw search results
            k: Number of results to return
        
        Returns:
            Filtered and ranked results
        """
        if not results:
            return []

        unique_by_doc = {}
        for result in results:
            doc_id = result["document_id"]
            if doc_id not in unique_by_doc:
                unique_by_doc[doc_id] = result

        filtered = list(unique_by_doc.values())
        
        filtered.sort(key=lambda x: x["score"])
        
        return filtered[:k]

    def get_context(self, query: str, k: int = 4) -> tuple[str, list[dict]]:
        """
        Get context string and source metadata for LLM.
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            Tuple of (context_string, sources_list)
        """
        results = self.retrieve(query, k=k)
        
        if not results:
            return "", []

        context_parts = []
        sources = []

        for i, result in enumerate(results):
            context_parts.append(
                f"[Document {i + 1}]\n{result['text'][:1000]}"
            )
            
            if result["document_id"] not in [s.get("document_id") for s in sources]:
                sources.append({
                    "document_id": result["document_id"],
                    "text": result["text"][:200],
                    "score": result["score"],
                })

        context = "\n\n".join(context_parts)
        
        return context, sources


def get_retrieval_service(user_id: str) -> RetrievalService:
    """Factory function to get retrieval service."""
    return RetrievalService(user_id)
