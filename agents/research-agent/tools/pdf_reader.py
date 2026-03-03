"""
PDF reading and parsing tools
"""

import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional
from utils.helpers import print_error, print_info


class PDFReader:
    """Handle PDF file reading and text extraction"""
    
    def __init__(self, filepath: str):
        """
        Initialize PDF reader
        
        Args:
            filepath: Path to PDF file
        """
        self.filepath = Path(filepath)
        
        if not self.filepath.exists():
            raise FileNotFoundError(f"PDF file not found: {filepath}")
        
        if not self.filepath.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {filepath}")
    
    def extract_text_pypdf2(self) -> str:
        """
        Extract text using PyPDF2
        
        Returns:
            Extracted text content
        """
        try:
            text_content = []
            
            with open(self.filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                print_info(f"Processing {num_pages} pages with PyPDF2...")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
            
            return "\n\n".join(text_content)
        
        except Exception as e:
            print_error(f"PyPDF2 extraction failed: {str(e)}")
            return ""
    
    def extract_text_pdfplumber(self) -> str:
        """
        Extract text using pdfplumber (better for complex layouts)
        
        Returns:
            Extracted text content
        """
        try:
            text_content = []
            
            with pdfplumber.open(self.filepath) as pdf:
                num_pages = len(pdf.pages)
                
                print_info(f"Processing {num_pages} pages with pdfplumber...")
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        text_content.append(text)
            
            return "\n\n".join(text_content)
        
        except Exception as e:
            print_error(f"pdfplumber extraction failed: {str(e)}")
            return ""
    
    def extract_text(self, method: str = "pdfplumber") -> str:
        """
        Extract text from PDF using specified method
        
        Args:
            method: Extraction method ('pdfplumber' or 'pypdf2')
            
        Returns:
            Extracted text content
        """
        if method == "pdfplumber":
            text = self.extract_text_pdfplumber()
            # Fallback to PyPDF2 if pdfplumber fails
            if not text:
                print_info("Falling back to PyPDF2...")
                text = self.extract_text_pypdf2()
        else:
            text = self.extract_text_pypdf2()
            # Fallback to pdfplumber if PyPDF2 fails
            if not text:
                print_info("Falling back to pdfplumber...")
                text = self.extract_text_pdfplumber()
        
        return text
    
    def get_metadata(self) -> Dict[str, any]:
        """
        Extract PDF metadata
        
        Returns:
            Dictionary containing metadata
        """
        try:
            with open(self.filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    'title': metadata.get('/Title', 'Unknown'),
                    'author': metadata.get('/Author', 'Unknown'),
                    'subject': metadata.get('/Subject', 'Unknown'),
                    'creator': metadata.get('/Creator', 'Unknown'),
                    'producer': metadata.get('/Producer', 'Unknown'),
                    'num_pages': len(pdf_reader.pages)
                }
        except Exception as e:
            print_error(f"Failed to extract metadata: {str(e)}")
            return {}
    
    def extract_structured_content(self) -> Dict[str, any]:
        """
        Extract both text and metadata in a structured format
        
        Returns:
            Dictionary with text content and metadata
        """
        metadata = self.get_metadata()
        text = self.extract_text()
        
        return {
            'metadata': metadata,
            'content': text,
            'filepath': str(self.filepath),
            'filename': self.filepath.name
        }


def read_pdf(filepath: str, include_metadata: bool = True) -> Dict[str, any]:
    """
    Convenience function to read PDF and extract content
    
    Args:
        filepath: Path to PDF file
        include_metadata: Whether to include metadata
        
    Returns:
        Dictionary with PDF content and optional metadata
    """
    reader = PDFReader(filepath)
    
    if include_metadata:
        return reader.extract_structured_content()
    else:
        return {
            'content': reader.extract_text(),
            'filepath': str(filepath)
        }