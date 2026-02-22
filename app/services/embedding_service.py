"""Embedding service for generating text embeddings."""

import os
from typing import Optional

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    """
    Service for generating text embeddings.
    
    Supports multiple embedding models:
    - OpenAI text-embedding-3-small (default)
    - OpenAI text-embedding-ada-002
    - HuggingFace sentence-transformers
    
    Design decision: Use OpenAI by default for quality,
    with HuggingFace as self-hosted alternative.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding service.
        
        Args:
            model_name: Override default embedding model
        """
        self.model_name = model_name or settings.openai_embedding_model
        self.embeddings = self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Initialize the embedding model."""
        if self.model_name.startswith("text-embedding-3") or self.model_name.startswith(
            "text-embedding-ada"
        ):
            return OpenAIEmbeddings(
                model=self.model_name,
                openai_api_key=settings.openai_api_key,
                dimensions=settings.openai_embedding_dimensions,
            )
        else:
            return HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of text strings
        
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """
        Generate embedding for a query.
        
        Args:
            text: Query string
        
        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)

    async def embed_documents_async(self, texts: list[str]) -> list[list[float]]:
        """
        Async wrapper for document embedding.
        
        Note: OpenAI SDK handles async internally using httpx.
        """
        return await self.embeddings.aembed_documents(texts)

    async def embed_query_async(self, text: str) -> list[float]:
        """
        Async wrapper for query embedding.
        
        Note: OpenAI SDK handles async internally using httpx.
        """
        return await self.embeddings.aembed_query(text)


def get_embedding_service() -> EmbeddingService:
    """Factory function to get embedding service instance."""
    return EmbeddingService()
