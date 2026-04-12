"""Unit tests for document parser utility."""

import pytest
import os
import tempfile

from app.utils.document_parser import DocumentParser, get_file_type


class TestDocumentParser:
    """Tests for DocumentParser class."""

    def test_get_file_type_pdf(self):
        """Test PDF file type detection."""
        assert get_file_type("document.pdf") == "pdf"
        assert get_file_type("DOCUMENT.PDF") == "pdf"

    def test_get_file_type_txt(self):
        """Test TXT file type detection."""
        assert get_file_type("readme.txt") == "text"
        assert get_file_type("notes.TXT") == "text"

    def test_get_file_type_md(self):
        """Test MD file type detection."""
        assert get_file_type("readme.md") == "markdown"
        assert get_file_type("notes.MD") == "markdown"

    def test_get_file_type_docx(self):
        """Test DOCX file type detection."""
        assert get_file_type("document.docx") == "docx"
        assert get_file_type("DOCUMENT.DOCX") == "docx"

    def test_get_file_type_unsupported(self):
        """Test unsupported file type."""
        assert get_file_type("document.exe") is None
        assert get_file_type("document") is None
        assert get_file_type("") is None

    def test_parse_text_file(self):
        """Test parsing text file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello, this is a test document.")
            temp_path = f.name

        try:
            content = DocumentParser.parse(temp_path, "txt")
            assert "Hello" in content
            assert "test document" in content
        finally:
            os.unlink(temp_path)

    def test_parse_unsupported_type(self):
        """Test parsing unsupported file type."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            DocumentParser.parse("test.exe", "exe")

    def test_supported_formats(self):
        """Test supported formats dictionary."""
        assert "pdf" in DocumentParser.SUPPORTED_FORMATS
        assert "txt" in DocumentParser.SUPPORTED_FORMATS
        assert "md" in DocumentParser.SUPPORTED_FORMATS
        assert "docx" in DocumentParser.SUPPORTED_FORMATS