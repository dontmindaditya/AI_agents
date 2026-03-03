"""
Data models for research papers
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PaperSource(str, Enum):
    """Source of the research paper"""
    FILE = "file"
    ARXIV = "arxiv"
    URL = "url"
    TEXT = "text"


class PaperMetadata(BaseModel):
    """Metadata extracted from paper"""
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    publication_date: Optional[str] = None
    venue: Optional[str] = None  # Conference/Journal name
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    

class MathematicalFormulation(BaseModel):
    """Mathematical equations and formulas"""
    equation_id: str
    latex_form: str
    description: Optional[str] = None
    variables: Dict[str, str] = Field(default_factory=dict)  # variable: description
    

class AlgorithmStep(BaseModel):
    """Individual step in the algorithm"""
    step_number: int
    description: str
    pseudocode: Optional[str] = None
    complexity: Optional[str] = None


class Paper(BaseModel):
    """Complete research paper model"""
    id: str = Field(default_factory=lambda: f"paper_{datetime.now().timestamp()}")
    source: PaperSource
    metadata: PaperMetadata
    
    # Content
    full_text: str
    sections: Dict[str, str] = Field(default_factory=dict)  # section_title: content
    
    # Extracted information
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    mathematical_formulations: List[MathematicalFormulation] = Field(default_factory=list)
    algorithm_steps: List[AlgorithmStep] = Field(default_factory=list)
    
    # Additional context
    related_work: Optional[str] = None
    datasets_mentioned: List[str] = Field(default_factory=list)
    code_snippets: List[Dict[str, str]] = Field(default_factory=list)
    figures_tables: List[str] = Field(default_factory=list)
    
    # Processing metadata
    created_at: datetime = Field(default_factory=datetime.now)
    file_path: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaperAnalysis(BaseModel):
    """Analysis result from Paper Analyzer Agent"""
    paper_id: str
    
    # Core analysis
    algorithm_name: str
    algorithm_type: str  # "supervised_learning", "optimization", "graph", etc.
    complexity_analysis: Dict[str, str] = Field(default_factory=dict)  # time, space
    
    # Technical details
    input_specification: str
    output_specification: str
    prerequisites: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    
    # Implementation hints
    key_data_structures: List[str] = Field(default_factory=list)
    critical_implementation_details: List[str] = Field(default_factory=list)
    edge_cases: List[str] = Field(default_factory=list)
    
    # References to paper content
    relevant_sections: List[str] = Field(default_factory=list)
    key_equations: List[str] = Field(default_factory=list)
    
    # Confidence and notes
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    analysis_notes: str = ""
    
    analyzed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }