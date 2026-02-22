"""Text chunking strategies for document processing."""

import re
from typing import Optional


class TextChunker:
    """
    Text chunker for splitting documents into smaller pieces.
    
    Supports multiple strategies:
    - Fixed size with overlap
    - Semantic chunking (by paragraphs)
    - Recursive splitting
    
    Design decision: We use a hybrid approach combining paragraph
    detection with size limits to maintain semantic coherence.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[list[str]] = None,
    ):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            separators: List of separators for splitting text
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ]

    def chunk_text(self, text: str) -> list[str]:
        """
        Split text into chunks using recursive approach.
        
        Args:
            text: Input text to chunk
        
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        chunks = []
        text = self._normalize_text(text)

        self._split_text(text, chunks)

        return [chunk.strip() for chunk in chunks if chunk.strip()]

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing excessive whitespace."""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)
        return text.strip()

    def _split_text(self, text: str, chunks: list[str]) -> None:
        """Recursively split text into chunks."""
        if len(text) <= self.chunk_size:
            chunks.append(text)
            return

        for separator in self.separators:
            if separator == "":
                chunks.append(text[: self.chunk_size])
                remaining = text[self.chunk_size :]
                if remaining:
                    self._split_text(remaining, chunks)
                return

            if separator in text:
                parts = text.split(separator)
                current_chunk = ""

                for part in parts:
                    test_chunk = current_chunk + separator + part if current_chunk else part

                    if len(test_chunk) <= self.chunk_size:
                        current_chunk = test_chunk
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        if len(part) > self.chunk_size:
                            self._split_text(part, chunks)
                            current_chunk = ""
                        else:
                            current_chunk = part

                if current_chunk:
                    chunks.append(current_chunk)

                return

    def chunk_by_paragraphs(self, text: str) -> list[str]:
        """
        Split text by paragraphs with size limits.
        
        Args:
            text: Input text
        
        Returns:
            List of paragraph-based chunks
        """
        if not text:
            return []

        paragraphs = re.split(r"\n\s*\n", text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                if len(para) > self.chunk_size:
                    chunks.extend(self.chunk_text(para))
                    current_chunk = ""
                else:
                    current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class SemanticChunker(TextChunker):
    """
    Semantic chunker that tries to maintain semantic coherence.
    
    Uses sentence detection and context preservation.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_sentences: int = 2,
    ):
        super().__init__(chunk_size, chunk_overlap)
        self.min_sentences = min_sentences
        self.sentence_pattern = re.compile(
            r"(?<=[.!?])\s+|(?<=\n)\s*",
            re.MULTILINE,
        )

    def chunk_text(self, text: str) -> list[str]:
        """Split text maintaining semantic boundaries."""
        if not text or not text.strip():
            return []

        sentences = self.sentence_pattern.split(text)
        chunks = []
        current_chunk = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            current_chunk.append(sentence)

            chunk_text = " ".join(current_chunk)
            if len(chunk_text) >= self.chunk_size or self._is_complete_thought(
                current_chunk
            ):
                chunks.append(chunk_text)
                
                overlap_text = " ".join(current_chunk[-2:])
                if len(overlap_text) <= self.chunk_overlap:
                    current_chunk = current_chunk[-2:]
                else:
                    current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return [chunk.strip() for chunk in chunks if chunk.strip()]

    def _is_complete_thought(self, sentences: list[str]) -> bool:
        """Check if sentences form a complete thought."""
        if len(sentences) < self.min_sentences:
            return False

        last_sentence = sentences[-1].strip()
        return last_sentence.endswith((".", "!", "?"))
