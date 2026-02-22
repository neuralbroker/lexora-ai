"""Celery worker configuration for async document processing."""

from celery import Celery
from celery.config import Config

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "lexora",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.document_processor"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=100,
)


@celery_app.task(bind=True)
def process_document_task(self, document_id: str, user_id: str):
    """
    Async task for processing documents.
    
    Args:
        document_id: ID of the document to process
        user_id: ID of the user who owns the document
    """
    import asyncio
    from sqlalchemy import select
    from app.schemas.database import async_session_maker, Document
    from app.services.document_service import get_document_service
    from app.schemas.database import User
    
    async def _process():
        async with async_session_maker() as db:
            result = await db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()
            
            if not document:
                return {"error": "Document not found"}
            
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            doc_service = get_document_service(db, user)
            
            try:
                await doc_service._process_document(document)
                document.status = "completed"
                await db.commit()
                return {"status": "completed", "document_id": document_id}
            except Exception as e:
                document.status = "failed"
                document.error_message = str(e)
                await db.commit()
                return {"status": "failed", "error": str(e)}
    
    return asyncio.run(_process())
