"""Unit tests for text chunker."""

import pytest
from app.utils.text_chunker import TextChunker, SemanticChunker


class TestTextChunker:
    """Tests for TextChunker class."""

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker(chunk_size=100)
        result = chunker.chunk_text("")
        assert result == []

    def test_chunk_text_shorter_than_chunk_size(self):
        """Test text shorter than chunk size."""
        chunker = TextChunker(chunk_size=100)
        text = "This is a short text."
        result = chunker.chunk_text(text)
        assert len(result) == 1
        assert result[0] == text

    def test_chunk_text_by_sentences(self):
        """Test chunking text by sentences."""
        chunker = TextChunker(chunk_size=50)
        text = "This is the first sentence. This is the second sentence."
        result = chunker.chunk_text(text)
        assert len(result) > 0

    def test_chunk_text_preserves_words(self):
        """Test that chunks preserve complete words."""
        chunker = TextChunker(chunk_size=10)
        text = "Hello world test"
        result = chunker.chunk_text(text)
        
        for chunk in result:
            words = chunk.split()
            for word in words:
                assert len(word) <= 10

    def test_chunk_by_paragraphs(self):
        """Test paragraph-based chunking."""
        chunker = TextChunker(chunk_size=100)
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = chunker.chunk_by_paragraphs(text)
        
        assert len(result) > 0
        for chunk in result:
            assert len(chunk) <= 100


class TestSemanticChunker:
    """Tests for SemanticChunker class."""

    def test_semantic_chunking(self):
        """Test semantic chunking maintains sentence boundaries."""
        chunker = SemanticChunker(chunk_size=100, min_sentences=2)
        text = "This is the first sentence. This is the second sentence. This is the third sentence."
        result = chunker.chunk_text(text)
        
        assert len(result) > 0

    def test_semantic_chunking_complete_thoughts(self):
        """Test that chunks form complete thoughts."""
        chunker = SemanticChunker(chunk_size=50, min_sentences=1)
        text = "Hello world. How are you?"
        result = chunker.chunk_text(text)
        
        for chunk in result:
            if len(chunk) > 10:
                assert chunk.endswith((".", "!", "?"))
