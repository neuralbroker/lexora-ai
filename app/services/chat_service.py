"""Chat service for handling conversations."""

from typing import AsyncGenerator, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.schemas.database import Conversation, Document, Message, User
from app.services.llm_service import get_llm_service
from app.services.retrieval_service import get_retrieval_service
from app.services.cache_service import get_cache_service

logger = get_logger(__name__)


class ChatService:
    """
    Service for handling chat operations.
    
    Features:
    - Conversation management
    - Message history
    - RAG-powered responses
    - Streaming responses
    - Source tracking
    
    Design decision: Orchestrates retrieval and LLM generation.
    """

    def __init__(
        self,
        db: AsyncSession,
        user: User,
    ):
        """
        Initialize chat service.
        
        Args:
            db: Database session
            user: Current user
        """
        self.db = db
        self.user = user

    async def create_message(
        self,
        content: str,
        conversation_id: Optional[str] = None,
        document_ids: Optional[list[str]] = None,
    ) -> tuple[Message, Message]:
        """
        Create and process a new message.
        
        Args:
            content: Message content
            conversation_id: Optional existing conversation
            document_ids: Optional document filter
        
        Returns:
            Tuple of (user_message, assistant_message)
        """
        logger.info(
            "chat_message_started",
            user_id=self.user.id,
            conversation_id=conversation_id,
        )

        conversation = await self._get_or_create_conversation(conversation_id)

        user_message = Message(
            id=str(uuid4()),
            conversation_id=conversation.id,
            user_id=self.user.id,
            role="user",
            content=content,
        )
        self.db.add(user_message)

        if not conversation.title:
            conversation.title = content[:50] + "..." if len(content) > 50 else content

        context, sources = await self._retrieve_context(
            content,
            document_ids,
        )

        chat_history = await self._get_chat_history(conversation.id)

        llm_service = get_llm_service()
        response = llm_service.generate(
            query=content,
            context=context,
            chat_history=chat_history,
        )

        assistant_message = Message(
            id=str(uuid4()),
            conversation_id=conversation.id,
            user_id=self.user.id,
            role="assistant",
            content=response,
            sources=sources,
        )
        self.db.add(assistant_message)

        await self.db.commit()
        await self.db.refresh(user_message)
        await self.db.refresh(assistant_message)

        logger.info(
            "chat_message_completed",
            user_id=self.user.id,
            conversation_id=conversation.id,
        )

        return user_message, assistant_message

    async def create_message_stream(
        self,
        content: str,
        conversation_id: Optional[str] = None,
        document_ids: Optional[list[str]] = None,
    ) -> AsyncGenerator[tuple[Message, str], None]:
        """
        Create and process a new message with streaming response.
        
        Args:
            content: Message content
            conversation_id: Optional existing conversation
            document_ids: Optional document filter
        
        Yields:
            Tuples of (user_message, response_chunk)
        """
        logger.info(
            "chat_stream_started",
            user_id=self.user.id,
            conversation_id=conversation_id,
        )

        conversation = await self._get_or_create_conversation(conversation_id)

        user_message = Message(
            id=str(uuid4()),
            conversation_id=conversation.id,
            user_id=self.user.id,
            role="user",
            content=content,
        )
        self.db.add(user_message)
        await self.db.commit()
        await self.db.refresh(user_message)

        if not conversation.title:
            conversation.title = content[:50] + "..." if len(content) > 50 else content

        context, sources = await self._retrieve_context(
            content,
            document_ids,
        )

        chat_history = await self._get_chat_history(conversation.id)

        llm_service = get_llm_service()
        
        full_response = ""
        async for chunk in llm_service.generate_stream(
            query=content,
            context=context,
            chat_history=chat_history,
        ):
            full_response += chunk
            yield user_message, chunk

        assistant_message = Message(
            id=str(uuid4()),
            conversation_id=conversation.id,
            user_id=self.user.id,
            role="assistant",
            content=full_response,
            sources=sources,
        )
        self.db.add(assistant_message)
        await self.db.commit()

        logger.info(
            "chat_stream_completed",
            user_id=self.user.id,
            conversation_id=conversation.id,
        )

    async def _retrieve_context(
        self,
        query: str,
        document_ids: Optional[list[str]] = None,
    ) -> tuple[str, list[dict]]:
        """Retrieve context from documents."""
        cache_service = get_cache_service()
        
        cache_key = f"retrieval:{self.user.id}:{hash(query)}"
        cached = await cache_service.get(cache_key)
        
        if cached:
            return cached["context"], cached["sources"]

        retrieval_service = get_retrieval_service(self.user.id)
        
        context, sources = retrieval_service.get_context(query, k=4)

        if document_ids:
            context, sources = retrieval_service.get_context(
                query,
                k=4,
            )
            context, sources = self._filter_by_documents(context, sources, document_ids)

        await cache_service.set(
            cache_key,
            {"context": context, "sources": sources},
            expire=3600,
        )

        return context, sources

    def _filter_by_documents(
        self,
        context: str,
        sources: list[dict],
        document_ids: list[str],
    ) -> tuple[str, list[dict]]:
        """Filter sources by document IDs."""
        filtered = [s for s in sources if s["document_id"] in document_ids]
        return context, filtered

    async def _get_or_create_conversation(
        self,
        conversation_id: Optional[str] = None,
    ) -> Conversation:
        """Get existing or create new conversation."""
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == self.user.id,
                )
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise NotFoundError("Conversation not found")
            return conversation

        conversation = Conversation(
            id=str(uuid4()),
            user_id=self.user.id,
            title="New Conversation",
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def _get_chat_history(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> list[tuple[str, str]]:
        """Get recent chat history."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()

        return [(msg.content, "") for msg in reversed(messages) if msg.role == "user"]

    async def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation:
        """Get conversation by ID."""
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == self.user.id,
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise NotFoundError("Conversation not found")

        return conversation

    async def list_conversations(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Conversation]:
        """List user's conversations."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == self.user.id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation and its messages."""
        conversation = await self.get_conversation(conversation_id)
        await self.db.delete(conversation)
        await self.db.commit()


def get_chat_service(
    db: AsyncSession,
    user: User,
) -> ChatService:
    """Factory function to get chat service."""
    return ChatService(db, user)
