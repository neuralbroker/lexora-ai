"""Unit tests for chat service behavior."""

from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.database import Conversation, Message, User, utc_now
from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_get_chat_history_pairs_user_and_assistant_turns(
    db_session: AsyncSession,
    test_user: User,
):
    """Chat history should include paired user and assistant messages."""
    conversation = Conversation(
        id="conversation-history-test",
        user_id=test_user.id,
        title="History test",
    )
    db_session.add(conversation)

    base_time = utc_now()
    db_session.add_all(
        [
            Message(
                id="message-1",
                conversation_id=conversation.id,
                user_id=test_user.id,
                role="user",
                content="What is Lexora?",
                created_at=base_time,
            ),
            Message(
                id="message-2",
                conversation_id=conversation.id,
                user_id=test_user.id,
                role="assistant",
                content="Lexora is a document QA platform.",
                created_at=base_time + timedelta(seconds=1),
            ),
            Message(
                id="message-3",
                conversation_id=conversation.id,
                user_id=test_user.id,
                role="user",
                content="How does retrieval work?",
                created_at=base_time + timedelta(seconds=2),
            ),
            Message(
                id="message-4",
                conversation_id=conversation.id,
                user_id=test_user.id,
                role="assistant",
                content="It searches embedded document chunks.",
                created_at=base_time + timedelta(seconds=3),
            ),
        ]
    )
    await db_session.commit()

    service = ChatService(db_session, test_user)
    history = await service._get_chat_history(conversation.id)

    assert history == [
        ("What is Lexora?", "Lexora is a document QA platform."),
        ("How does retrieval work?", "It searches embedded document chunks."),
    ]


@pytest.mark.asyncio
async def test_get_chat_history_ignores_unanswered_user_message(
    db_session: AsyncSession,
    test_user: User,
):
    """The in-flight user message should not be passed as a blank assistant turn."""
    conversation = Conversation(
        id="conversation-pending-test",
        user_id=test_user.id,
        title="Pending test",
    )
    db_session.add(conversation)

    base_time = utc_now()
    db_session.add_all(
        [
            Message(
                id="message-pending-1",
                conversation_id=conversation.id,
                user_id=test_user.id,
                role="user",
                content="First question",
                created_at=base_time,
            ),
            Message(
                id="message-pending-2",
                conversation_id=conversation.id,
                user_id=test_user.id,
                role="assistant",
                content="First answer",
                created_at=base_time + timedelta(seconds=1),
            ),
            Message(
                id="message-pending-3",
                conversation_id=conversation.id,
                user_id=test_user.id,
                role="user",
                content="Pending question",
                created_at=base_time + timedelta(seconds=2),
            ),
        ]
    )
    await db_session.commit()

    service = ChatService(db_session, test_user)
    history = await service._get_chat_history(conversation.id)

    assert history == [("First question", "First answer")]
