"""Document service for handling document operations."""

import os
from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.schemas.database import Document, User
from app.services.embedding_service import get_embedding_service
from app.services.vector_service import get_vector_store
from app.utils.document_parser import DocumentParser, get_file_type, save_uploaded_file
from app.utils.text_chunker import TextChunker

settings = get_settings()
logger = get_logger(__name__)


class DocumentService:
    """
    Service for handling document operations.
    
    Features:
    - File upload and storage
    - Text extraction
    - Chunking
    - Embedding generation
    - Vector storage
    
    Design decision: This is the main orchestrator for the
    ingestion pipeline. For production, move heavy processing
    to Celery workers.
    """

    def __init__(
        self,
        db: AsyncSession,
        user: User,
        chunker: Optional[TextChunker] = None,
        embedding_service=None,
    ):
        """
        Initialize document service.
        
        Args:
            db: Database session
            user: Current user
            chunker: Optional text chunker
            embedding_service: Optional embedding service
        """
        self.db = db
        self.user = user
        self.chunker = chunker or TextChunker(
            chunk_size=1000,
            chunk_overlap=200,
        )
        self.embedding_service = embedding_service or get_embedding_service()

    async def upload_document(
        self,
        file_content: bytes,
        filename: str,
    ) -> Document:
        """
        Upload and process a document.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
        
        Returns:
            Created document record
        """
        logger.info("document_upload_started", user_id=self.user.id, filename=filename)

        file_type = self._validate_file(filename)
        file_size = len(file_content)

        file_path = await save_uploaded_file(
            file_content,
            filename,
            settings.upload_dir,
        )

        document = Document(
            id=str(uuid4()),
            user_id=self.user.id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            status="processing",
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        try:
            await self._process_document(document)
            document.status = "completed"
            logger.info(
                "document_processed",
                user_id=self.user.id,
                document_id=document.id,
                chunks=document.chunk_count,
            )
        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)
            logger.error(
                "document_processing_failed",
                user_id=self.user.id,
                document_id=document.id,
                error=str(e),
            )

        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def _process_document(self, document: Document) -> None:
        """Process document: extract text, chunk, embed, store."""
        text = await DocumentParser.parse_async(
            document.file_path,
            document.file_type,
        )

        chunks = self.chunker.chunk_text(text)

        if not chunks:
            raise ValidationError("No text content found in document")

        vectors = self.embedding_service.embed_documents(chunks)

        vector_store = get_vector_store(self.user.id)
        
        vector_ids = vector_store.add_vectors(
            vectors=vectors,
            documents=chunks,
            document_ids=[document.id] * len(chunks),
        )

        document.chunk_count = len(chunks)
        document.vector_ids = vector_ids

    async def get_document(self, document_id: str) -> Document:
        """Get a document by ID."""
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == self.user.id,
            )
        )
        document = result.scalar_one_or_none()

        if not document:
            raise NotFoundError(f"Document not found: {document_id}")

        return document

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Document]:
        """List user's documents."""
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == self.user.id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_document(self, document_id: str) -> None:
        """Delete a document and its vectors."""
        document = await self.get_document(document_id)

        try:
            vector_store = get_vector_store(self.user.id)
            vector_store.delete_vectors(document_id)
        except Exception as e:
            logger.warning(
                "vector_deletion_failed",
                document_id=document_id,
                error=str(e),
            )

        await self.db.delete(document)
        await self.db.commit()

        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            logger.warning(
                "file_deletion_failed",
                file_path=document.file_path,
                error=str(e),
            )

    def _validate_file(self, filename: str) -> str:
        """Validate file type."""
        file_type = get_file_type(filename)
        
        if not file_type:
            raise ValidationError(
                f"Unsupported file type. Allowed: {', '.join(settings.allowed_extensions)}"
            )

        ext = file_type.lower()
        if ext not in settings.allowed_extensions:
            raise ValidationError(
                f"File extension not allowed. Allowed: {', '.join(settings.allowed_extensions)}"
            )

        return ext


def get_document_service(
    db: AsyncSession,
    user: User,
) -> DocumentService:
    """Factory function to get document service."""
    return DocumentService(db, user)
