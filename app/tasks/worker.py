"""Celery worker configuration for async document processing."""

from app.tasks.celery_app import celery_app


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
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()

            if not document:
                return {"error": "Document not found"}

            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()

            if not user:
                return {"error": "User not found"}

            doc_service = get_document_service(db, user)

            await doc_service.process_document(document)
            return {
                "status": document.status,
                "document_id": document_id,
                "error": document.error_message,
            }

    return asyncio.run(_process())
