"""Document endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.deps import DBSession, CurrentUser
from app.models.user import DocumentResponse, DocumentStatus, DocumentUploadResponse
from app.schemas.database import Document, User
from app.services.document_service import get_document_service

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> Document:
    """
    Upload and process a document.
    
    Supports PDF, TXT, MD, and DOCX files.
    Processing is done asynchronously.
    """
    if file.size and file.size > settings.max_file_size:
        raise ValidationError(
            f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024}MB"
        )

    content = await file.read()
    
    doc_service = get_document_service(db, current_user)
    document = await doc_service.upload_document(content, file.filename)

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        message="Document uploaded successfully. Processing in background.",
        created_at=document.created_at,
    )


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: DBSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> List[Document]:
    """List user's documents."""
    doc_service = get_document_service(db, current_user)
    documents = await doc_service.list_documents(skip=skip, limit=limit)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: DBSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> Document:
    """Get document details."""
    doc_service = get_document_service(db, current_user)
    return await doc_service.get_document(document_id)


@router.get("/{document_id}/status", response_model=DocumentStatus)
async def get_document_status(
    document_id: str,
    db: DBSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> Document:
    """Get document processing status."""
    doc_service = get_document_service(db, current_user)
    document = await doc_service.get_document(document_id)
    return DocumentStatus(
        id=document.id,
        status=document.status,
        chunk_count=document.chunk_count,
        error_message=document.error_message,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: DBSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """Delete a document and its vectors."""
    doc_service = get_document_service(db, current_user)
    await doc_service.delete_document(document_id)
