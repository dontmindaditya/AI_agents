"""
Data models for generated code outputs
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProgrammingLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"


class CodeQuality(str, Enum):
    """Code quality assessment"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    NEEDS_IMPROVEMENT = "needs_improvement"


class ModuleStructure(BaseModel):
    """Structure of a code module/file"""
    file_name: str
    file_path: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)


class FunctionSignature(BaseModel):
    """Function/method signature"""
    name: str
    parameters: List[Dict[str, str]] = Field(default_factory=list)  # [{name, type, description}]
    return_type: str
    description: str
    complexity: Optional[str] = None


class ImplementationPlan(BaseModel):
    """Design plan from Algorithm Designer Agent"""
    paper_id: str
    
    # Architecture
    modules: List[ModuleStructure] = Field(default_factory=list)
    main_algorithm_file: str
    
    # Function designs
    function_signatures: List[FunctionSignature] = Field(default_factory=list)
    
    # Data structures
    data_structures: Dict[str, str] = Field(default_factory=dict)  # name: description
    class_hierarchy: Optional[str] = None  # Textual description or diagram
    
    # Implementation approach
    implementation_steps: List[str] = Field(default_factory=list)
    required_libraries: List[str] = Field(default_factory=list)
    
    # Testing strategy
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    testing_approach: str = ""
    
    # Notes
    design_rationale: str = ""
    optimization_opportunities: List[str] = Field(default_factory=list)
    potential_challenges: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CodeFile(BaseModel):
    """Individual code file"""
    file_name: str
    file_path: str
    language: ProgrammingLanguage
    code: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    line_count: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.code:
            self.line_count = len(self.code.split('\n'))


class TestFile(BaseModel):
    """Test file for generated code"""
    file_name: str
    file_path: str
    language: ProgrammingLanguage
    code: str
    test_count: int = 0
    coverage_estimate: Optional[float] = None


class Documentation(BaseModel):
    """Documentation for generated code"""
    readme: str
    api_docs: Optional[str] = None
    usage_examples: List[str] = Field(default_factory=list)
    installation_instructions: str = ""


class CodeReviewResult(BaseModel):
    """Results from Code Reviewer Agent"""
    
    # Review findings
    bugs_found: List[Dict[str, str]] = Field(default_factory=list)  # [{location, description, severity}]
    optimizations: List[Dict[str, str]] = Field(default_factory=list)  # [{location, suggestion, impact}]
    style_issues: List[str] = Field(default_factory=list)
    
    # Improvements made
    fixes_applied: List[str] = Field(default_factory=list)
    refactorings: List[str] = Field(default_factory=list)
    
    # Quality assessment
    quality_score: CodeQuality
    correctness_verification: str
    performance_analysis: str
    
    # Testing
    test_coverage: float = Field(ge=0.0, le=100.0, default=0.0)
    edge_cases_covered: List[str] = Field(default_factory=list)
    
    reviewed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CodeOutput(BaseModel):
    """Final code output from the agent system"""
    id: str = Field(default_factory=lambda: f"code_{datetime.now().timestamp()}")
    paper_id: str
    
    # Language and framework
    language: ProgrammingLanguage
    framework: Optional[str] = None  # "pytorch", "tensorflow", "numpy", etc.
    
    # Generated code
    code_files: List[CodeFile] = Field(default_factory=list)
    test_files: List[TestFile] = Field(default_factory=list)
    documentation: Documentation
    
    # Dependencies
    requirements: List[str] = Field(default_factory=list)
    system_requirements: List[str] = Field(default_factory=list)
    
    # Metadata
    implementation_plan: Optional[ImplementationPlan] = None
    review_result: Optional[CodeReviewResult] = None
    
    # Execution info
    total_lines: int = 0
    estimated_complexity: str = ""
    performance_notes: str = ""
    
    # Status
    is_validated: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    generation_time: Optional[float] = None  # seconds
    
    def __init__(self, **data):
        super().__init__(**data)
        self.total_lines = sum(f.line_count for f in self.code_files)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }