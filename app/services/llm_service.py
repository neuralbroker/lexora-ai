"""LLM service for generating responses using OpenAI."""

from typing import AsyncGenerator, Optional

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class LLMService:
    """
    Service for generating responses using LLMs.
    
    Features:
    - OpenAI GPT integration
    - Streaming responses
    - Configurable parameters
    - Error handling
    
    Design decision: Use LangChain for abstraction.
    For production, add:
    - Fallback models
    - Circuit breakers
    - Response caching
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize LLM service.
        
        Args:
            model_name: Override default model
            temperature: Override default temperature
            max_tokens: Override default max tokens
        """
        self.model_name = model_name or settings.openai_model
        self.temperature = temperature or settings.openai_temperature
        self.max_tokens = max_tokens or settings.openai_max_tokens
        self.llm = self._initialize_llm()

    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize OpenAI chat model."""
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=settings.openai_api_key,
            streaming=True,
        )

    def generate(
        self,
        query: str,
        context: str,
        chat_history: Optional[list[tuple[str, str]]] = None,
    ) -> str:
        """
        Generate response for a query with context.
        
        Args:
            query: User question
            context: Retrieved context from documents
            chat_history: Previous conversation history
        
        Returns:
            Generated response
        """
        prompt = self._build_prompt(query, context, chat_history)
        
        logger.info("llm_generation_started", query=query[:100])

        messages = [
            SystemMessage(
                content="You are a helpful AI assistant that answers questions "
                "based on the provided context from documents. "
                "Always base your answers on the provided context. "
                "If the context doesn't contain enough information to answer "
                "the question, say so clearly."
            ),
            HumanMessage(content=prompt),
        ]

        response = self.llm.invoke(messages)
        
        logger.info("llm_generation_completed", query=query[:100])
        
        return response.content

    async def generate_stream(
        self,
        query: str,
        context: str,
        chat_history: Optional[list[tuple[str, str]]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response for a query.
        
        Args:
            query: User question
            context: Retrieved context from documents
            chat_history: Previous conversation history
        
        Yields:
            Response chunks
        """
        prompt = self._build_prompt(query, context, chat_history)
        
        logger.info("llm_stream_started", query=query[:100])

        messages = [
            SystemMessage(
                content="You are a helpful AI assistant that answers questions "
                "based on the provided context from documents. "
                "Always base your answers on the provided context. "
                "If the context doesn't contain enough information to answer "
                "the question, say so clearly."
            ),
            HumanMessage(content=prompt),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

    def _build_prompt(
        self,
        query: str,
        context: str,
        chat_history: Optional[list[tuple[str, str]]] = None,
    ) -> str:
        """Build prompt with context and history."""
        history_text = ""
        if chat_history:
            history_text = "\n".join(
                f"Human: {q}\nAssistant: {a}" for q, a in chat_history[-5:]
            )

        prompt = f"""Context from documents:
{context}

{'Previous conversation:' if chat_history else ''}
{history_text}

Current question: {query}

Please provide a helpful answer based on the context above. 
If the context doesn't contain relevant information, say so."""
        
        return prompt


def get_llm_service() -> LLMService:
    """Factory function to get LLM service."""
    return LLMService()
