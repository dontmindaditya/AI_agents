"""
Tools package for research agent
"""

from .pdf_reader import PDFReader, read_pdf
from .web_search import WebSearchTool, SimpleWebSearch, create_search_tool
from .content_processor import (
    ContentProcessor,
    clean_text,
    extract_sections,
    extract_key_phrases,
    summarize_text,
    chunk_text
)

__all__ = [
    'PDFReader',
    'read_pdf',
    'WebSearchTool',
    'SimpleWebSearch',
    'create_search_tool',
    'ContentProcessor',
    'clean_text',
    'extract_sections',
    'extract_key_phrases',
    'summarize_text',
    'chunk_text'
]