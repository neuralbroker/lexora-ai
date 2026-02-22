"""Chat endpoints with streaming support."""

import json
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.deps import DBSession, CurrentUser
from app.models.user import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)
from app.schemas.database import Conversation, Message, User
from app.services.chat_service import get_chat_service

logger = get_logger(__name__)

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> dict:
    """
    Send a message and get a response (non-streaming).
    """
    chat_service = get_chat_service(db, current_user)

    user_message, assistant_message = await chat_service.create_message(
        content=request.message,
        conversation_id=request.conversation_id,
        document_ids=request.document_ids,
    )

    return ChatResponse(
        message=assistant_message.content,
        conversation_id=user_message.conversation_id,
        sources=assistant_message.sources or [],
    )


@router.post("/stream")
async def send_message_stream(
    request: ChatRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """
    Send a message and get a streaming response.
    
    Uses Server-Sent Events (SSE) for streaming.
    """
    chat_service = get_chat_service(db, current_user)

    async def generate():
        conversation_id = None
        
        async for user_msg, chunk in chat_service.create_message_stream(
            content=request.message,
            conversation_id=request.conversation_id,
            document_ids=request.document_ids,
        ):
            conversation_id = user_msg.conversation_id
            
            data = json.dumps({
                "type": "chunk",
                "content": chunk,
                "conversation_id": conversation_id,
            })
            yield f"data: {data}\n\n"

        data = json.dumps({"type": "done", "conversation_id": conversation_id})
        yield f"data: {data}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: DBSession,
    current_user: CurrentUser,
) -> List[Conversation]:
    """List user's conversations."""
    chat_service = get_chat_service(db, current_user)
    return await chat_service.list_conversations(skip=skip, limit=limit)


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Conversation:
    """Create a new conversation."""
    from uuid import uuid4
    
    conversation = Conversation(
        id=str(uuid4()),
        user_id=current_user.id,
        title=request.title or "New Conversation",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.get("/conversations/{conversation_id}", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    db: DBSession,
    current_user: CurrentUser,
) -> List[Message]:
    """Get messages in a conversation."""
    chat_service = get_chat_service(db, current_user)
    conversation = await chat_service.get_conversation(conversation_id)
    
    from sqlalchemy import select
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return result.scalars().all()


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Delete a conversation."""
    chat_service = get_chat_service(db, current_user)
    await chat_service.delete_conversation(conversation_id)
