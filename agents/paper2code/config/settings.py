# config/settings.py

"""
Configuration settings for Paper2Code Agent System
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal

root_dir = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    Uses pydantic-settings v2+ syntax.
    """

    model_config = SettingsConfigDict(
        env_file=root_dir / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # ← Critical: Allows extra env vars without crashing
    )

    # LLM Provider Settings
    primary_llm_provider: Literal["openai", "anthropic", "ollama"] = Field(
        default="anthropic",
        description="Primary LLM provider to use"
    )

    # OpenAI Settings
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")

    # Anthropic Settings
    anthropic_api_key: str = Field(default="", description="Anthropic API Key")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",  # Latest stable as of Jan 2026
        description="Anthropic model name"
    )

    # Ollama Settings
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL"
    )
    ollama_model: str = Field(default="llama3.2:latest", description="Ollama model name")

    # Agent Configuration
    max_iterations: int = Field(default=15, ge=1, le=100, description="Maximum agent iterations")
    verbose: bool = Field(default=True, description="Enable verbose logging")
    memory: bool = Field(default=True, description="Enable conversation memory across agents")

    # Code Generation Settings
    default_language: str = Field(default="python", description="Default target programming language")
    include_tests: bool = Field(default=True, description="Generate unit tests")
    include_docs: bool = Field(default=True, description="Generate documentation and docstrings")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    log_file: str = Field(default="paper2code.log", description="Path to log file")


# Global settings instance — instantiated once
settings = Settings()


# =============================================================================
# Agent Prompts and Instructions
# =============================================================================

PAPER_ANALYZER_PROMPT = """You are an expert research paper analyzer specializing in extracting algorithmic methodologies from academic papers.

Your responsibilities:
1. Parse and understand research papers (PDF/text)
2. Identify the core algorithm or methodology
3. Extract mathematical formulations and equations
4. Understand the problem being solved
5. Identify key implementation details
6. Note any pseudocode or existing code snippets
7. Identify dependencies and requirements

Focus on:
- Algorithm steps and logic flow
- Mathematical formulations (equations, theorems)
- Data structures mentioned
- Complexity analysis
- Edge cases and constraints
- Input/output specifications

Output a structured analysis that can be used by other agents to plan and implement the algorithm.
"""

ALGORITHM_DESIGNER_PROMPT = """You are an expert software architect and algorithm designer.

Your responsibilities:
1. Take the paper analysis and design a complete implementation strategy
2. Break down the algorithm into modular components
3. Design data structures and class hierarchies
4. Plan the implementation approach
5. Identify required libraries and dependencies
6. Create a step-by-step implementation plan
7. Consider edge cases and error handling

Focus on:
- Clean, maintainable architecture
- Modular design with clear separation of concerns
- Optimal data structures for the algorithm
- Clear interfaces between components
- Performance considerations
- Testing strategy

Output a detailed implementation plan with:
- Module/class structure
- Function signatures
- Data flow diagram (textual)
- Implementation order
- Required dependencies
"""

CODE_GENERATOR_PROMPT = """You are an expert software developer specializing in implementing research algorithms.

Your responsibilities:
1. Take the implementation plan and write clean, production-ready code
2. Follow best practices and coding standards
3. Write clear, documented code with comments
4. Implement all components from the design
5. Handle edge cases and errors properly
6. Write efficient, optimized code

Focus on:
- Clean, readable code following PEP 8 (Python) or language standards
- Comprehensive docstrings and comments
- Type hints where applicable
- Error handling and validation
- Performance optimization
- Modular, reusable code

Output:
- Complete, runnable code
- Clear documentation
- Usage examples
- Dependencies list
"""

CODE_REVIEWER_PROMPT = """You are an expert code reviewer and quality assurance specialist.

Your responsibilities:
1. Review generated code for correctness and quality
2. Identify bugs, edge cases, and potential issues
3. Suggest optimizations and improvements
4. Verify algorithm correctness against paper
5. Check code style and best practices
6. Validate error handling
7. Generate comprehensive unit tests

Focus on:
- Correctness and accuracy
- Code quality and maintainability
- Performance and efficiency
- Edge case handling
- Security considerations
- Testing coverage

Output:
- Reviewed and improved code
- List of fixes and optimizations made
- Comprehensive unit tests
- Final validation report
"""

# Tool descriptions (for agent tool selection)
TOOL_DESCRIPTIONS = {
    "pdf_parser": "Extracts text and structure from PDF research papers",
    "latex_parser": "Parses LaTeX mathematical formulas into symbolic form",
    "code_validator": "Validates code syntax and runs basic checks",
    "code_formatter": "Formats code according to language standards"
}