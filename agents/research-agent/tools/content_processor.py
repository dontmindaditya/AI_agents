"""
Content processing utilities
"""

import re
from typing import List, Dict


class ContentProcessor:
    """Process and clean text content"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """
        Extract sections from structured text
        
        Args:
            text: Input text with headers
            
        Returns:
            Dictionary mapping section names to content
        """
        sections = {}
        current_section = "introduction"
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            # Check if line is a header (simple heuristic)
            if line.strip() and (line.isupper() or line.strip().endswith(':') or 
                               line.startswith('#')):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip().rstrip(':').lower()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def extract_key_phrases(text: str, min_length: int = 3) -> List[str]:
        """
        Extract key phrases from text (simple implementation)
        
        Args:
            text: Input text
            min_length: Minimum word length for phrases
            
        Returns:
            List of key phrases
        """
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'their', 'them'
        }
        
        # Extract sentences
        sentences = re.split(r'[.!?]+', text)
        
        key_phrases = []
        for sentence in sentences:
            words = sentence.lower().split()
            
            # Filter out stop words and short words
            filtered_words = [w for w in words if w not in stop_words and len(w) >= min_length]
            
            if len(filtered_words) >= 2:
                phrase = ' '.join(filtered_words[:5])  # Take up to 5 words
                if phrase:
                    key_phrases.append(phrase)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_phrases = []
        for phrase in key_phrases:
            if phrase not in seen:
                seen.add(phrase)
                unique_phrases.append(phrase)
        
        return unique_phrases[:20]  # Return top 20
    
    @staticmethod
    def summarize_text(text: str, max_sentences: int = 5) -> str:
        """
        Create a simple extractive summary
        
        Args:
            text: Input text
            max_sentences: Maximum sentences in summary
            
        Returns:
            Summary text
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences) + '.'
        
        # Simple heuristic: take first sentence, last sentence, and middle sentences
        summary_sentences = []
        summary_sentences.append(sentences[0])
        
        # Add middle sentences
        middle_start = len(sentences) // 3
        middle_end = 2 * len(sentences) // 3
        
        for i in range(middle_start, middle_end):
            if len(summary_sentences) < max_sentences - 1:
                summary_sentences.append(sentences[i])
        
        # Add last sentence
        if len(summary_sentences) < max_sentences:
            summary_sentences.append(sentences[-1])
        
        return '. '.join(summary_sentences) + '.'
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end within last 100 chars
                last_period = text[max(start, end-100):end].rfind('.')
                if last_period != -1:
                    end = max(start, end-100) + last_period + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks


# Create singleton instance
content_processor = ContentProcessor()


def clean_text(text: str) -> str:
    """Convenience function for text cleaning"""
    return content_processor.clean_text(text)


def extract_sections(text: str) -> Dict[str, str]:
    """Convenience function for section extraction"""
    return content_processor.extract_sections(text)


def extract_key_phrases(text: str) -> List[str]:
    """Convenience function for key phrase extraction"""
    return content_processor.extract_key_phrases(text)


def summarize_text(text: str, max_sentences: int = 5) -> str:
    """Convenience function for text summarization"""
    return content_processor.summarize_text(text, max_sentences)


def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Convenience function for text chunking"""
    return content_processor.chunk_text(text, chunk_size)