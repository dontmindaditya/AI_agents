"""
PDF parsing tool for extracting text and structure from research papers
"""
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from utils.logger import logger


class PDFParser:
    """Extract text, structure, and metadata from PDF research papers"""
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDF parser
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.doc = None
        self.text = ""
        self.metadata = {}
        self.sections = {}
        
    def extract_all(self) -> Dict:
        """
        Extract all information from PDF
        
        Returns:
            Dictionary with text, metadata, and sections
        """
        logger.info(f"Parsing PDF: {self.pdf_path.name}")
        
        try:
            # Extract with PyMuPDF (better for layout)
            self.doc = fitz.open(self.pdf_path)
            self.text = self._extract_text_pymupdf()
            self.metadata = self._extract_metadata()
            
            # Try to extract sections
            self.sections = self._extract_sections()
            
            return {
                "text": self.text,
                "metadata": self.metadata,
                "sections": self.sections,
                "page_count": len(self.doc)
            }
        
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}", exc=e)
            # Fallback to pdfplumber
            return self._extract_with_pdfplumber()
        
        finally:
            if self.doc:
                self.doc.close()
    
    def _extract_text_pymupdf(self) -> str:
        """Extract text using PyMuPDF"""
        full_text = []
        
        for page_num, page in enumerate(self.doc, 1):
            text = page.get_text()
            full_text.append(f"--- Page {page_num} ---\n{text}")
        
        return "\n\n".join(full_text)
    
    def _extract_with_pdfplumber(self) -> Dict:
        """Fallback extraction using pdfplumber"""
        logger.info("Using pdfplumber fallback")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            text_parts = []
            
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return {
                "text": "\n\n".join(text_parts),
                "metadata": pdf.metadata or {},
                "sections": {},
                "page_count": len(pdf.pages)
            }
    
    def _extract_metadata(self) -> Dict:
        """Extract PDF metadata"""
        metadata = {}
        
        if self.doc and self.doc.metadata:
            metadata = {
                "title": self.doc.metadata.get("title", ""),
                "author": self.doc.metadata.get("author", ""),
                "subject": self.doc.metadata.get("subject", ""),
                "creator": self.doc.metadata.get("creator", ""),
                "producer": self.doc.metadata.get("producer", ""),
                "creation_date": self.doc.metadata.get("creationDate", ""),
            }
        
        return metadata
    
    def _extract_sections(self) -> Dict[str, str]:
        """
        Attempt to extract paper sections (Abstract, Introduction, etc.)
        
        Returns:
            Dictionary mapping section names to content
        """
        sections = {}
        
        # Common section headers in research papers
        section_patterns = [
            r"^(?:1\.?\s*)?Abstract",
            r"^(?:\d+\.?\s*)?Introduction",
            r"^(?:\d+\.?\s*)?Related Work",
            r"^(?:\d+\.?\s*)?Methodology",
            r"^(?:\d+\.?\s*)?Method",
            r"^(?:\d+\.?\s*)?Approach",
            r"^(?:\d+\.?\s*)?Experiments?",
            r"^(?:\d+\.?\s*)?Results?",
            r"^(?:\d+\.?\s*)?Discussion",
            r"^(?:\d+\.?\s*)?Conclusion",
            r"^(?:\d+\.?\s*)?References",
            r"^(?:\d+\.?\s*)?Algorithm",
        ]
        
        lines = self.text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches any section header
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = re.sub(r'^\d+\.?\s*', '', line)
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def extract_equations(self) -> List[str]:
        """
        Extract mathematical equations (basic extraction)
        
        Returns:
            List of equation strings
        """
        equations = []
        
        # Look for common equation patterns
        equation_patterns = [
            r'\$\$.*?\$\$',  # LaTeX display equations
            r'\$.*?\$',      # LaTeX inline equations
            r'\\begin\{equation\}.*?\\end\{equation\}',
            r'\\begin\{align\}.*?\\end\{align\}',
        ]
        
        for pattern in equation_patterns:
            matches = re.findall(pattern, self.text, re.DOTALL)
            equations.extend(matches)
        
        return equations
    
    def extract_tables(self) -> List[Dict]:
        """
        Extract tables from PDF
        
        Returns:
            List of table data
        """
        tables = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    for table_data in page_tables:
                        tables.append({
                            "page": page_num,
                            "data": table_data
                        })
        except Exception as e:
            logger.warning(f"Could not extract tables: {str(e)}")
        
        return tables
    
    @staticmethod
    def extract_from_text(text: str) -> Dict:
        """
        Parse text directly without PDF
        
        Args:
            text: Raw text content
            
        Returns:
            Dictionary with parsed content
        """
        return {
            "text": text,
            "metadata": {},
            "sections": {},
            "page_count": 0
        }


def parse_pdf(pdf_path: str) -> Dict:
    """
    Convenience function to parse a PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Parsed content dictionary
    """
    parser = PDFParser(pdf_path)
    return parser.extract_all()