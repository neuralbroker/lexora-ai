"""Document parsing utilities for extracting text from various file formats."""

import io
import os
from typing import Optional
from pathlib import Path

import aiofiles
from pypdf import PdfReader
from docx import Document as DocxDocument

from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentParser:
    """
    Document parser for extracting text from various file formats.
    
    Supports:
    - PDF files (.pdf)
    - Plain text (.txt)
    - Markdown (.md)
    - Word documents (.docx)
    
    Design decision: Each parser is isolated to handle failures gracefully
    without affecting other formats.
    """

    SUPPORTED_FORMATS = {
        "pdf": "pdf",
        "txt": "text",
        "md": "markdown",
        "docx": "docx",
    }

    @classmethod
    def parse(cls, file_path: str, file_type: str) -> str:
        """
        Parse a document and extract text.
        
        Args:
            file_path: Path to the file
            file_type: Type of the file (pdf, txt, md, docx)
        
        Returns:
            Extracted text content
        
        Raises:
            ValueError: If file type is not supported
        """
        parser_map = {
            "pdf": cls._parse_pdf,
            "txt": cls._parse_text,
            "md": cls._parse_text,
            "docx": cls._parse_docx,
        }

        parser = parser_map.get(file_type.lower())
        if not parser:
            raise ValueError(f"Unsupported file type: {file_type}")

        return parser(file_path)

    @classmethod
    async def parse_async(cls, file_path: str, file_type: str) -> str:
        """Async wrapper for document parsing."""
        return cls.parse(file_path, file_type)

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """
        Parse PDF file and extract text.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text
        """
        try:
            text_parts = []
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error("pdf_parse_error", file_path=file_path, error=str(e))
            raise ValueError(f"Failed to parse PDF: {str(e)}") from e

    @staticmethod
    def _parse_text(file_path: str) -> str:
        """
        Parse plain text or markdown file.
        
        Args:
            file_path: Path to text file
        
        Returns:
            File content
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            logger.error("text_parse_error", file_path=file_path, error=str(e))
            raise ValueError(f"Failed to parse text file: {str(e)}") from e

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """
        Parse Word document.
        
        Args:
            file_path: Path to DOCX file
        
        Returns:
            Extracted text
        """
        try:
            doc = DocxDocument(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error("docx_parse_error", file_path=file_path, error=str(e))
            raise ValueError(f"Failed to parse DOCX: {str(e)}") from e

    @classmethod
    def get_file_type(cls, filename: str) -> Optional[str]:
        """
        Determine file type from filename.
        
        Args:
            filename: Name of the file
        
        Returns:
            File type or None if unsupported
        """
        ext = Path(filename).suffix.lower().lstrip(".")
        return cls.SUPPORTED_FORMATS.get(ext)


async def save_uploaded_file(
    content: bytes,
    filename: str,
    upload_dir: str,
) -> str:
    """
    Save uploaded file to disk.
    
    Args:
        content: File content as bytes
        filename: Original filename
        upload_dir: Directory to save files
    
    Returns:
        Path to saved file
    """
    os.makedirs(upload_dir, exist_ok=True)
    
    from datetime import datetime
    import uuid
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{timestamp}_{unique_id}_{filename}"
    
    file_path = os.path.join(upload_dir, safe_filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    return file_path
