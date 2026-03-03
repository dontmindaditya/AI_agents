"""
Orchestrator - Coordinates all agents in the Paper2Code pipeline
"""
from crewai import Crew, Process
from typing import Optional, Dict, Callable
from pathlib import Path
import time

from models import Paper, PaperSource, PaperMetadata, CodeOutput
from tools import PDFParser
from .paper_analyzer import PaperAnalyzerAgent
from .algorithm_designer import AlgorithmDesignerAgent
from .code_generator import CodeGeneratorAgent
from .code_reviewer import CodeReviewerAgent
from config import settings
from utils.logger import logger, log_agent_step, log_success, log_error


class Paper2CodeOrchestrator:
    """Orchestrates the entire Paper-to-Code conversion pipeline"""
    
    def __init__(self, llm=None, progress_callback: Optional[Callable] = None):
        """
        Initialize orchestrator with all agents
        
        Args:
            llm: Language model instance to use for all agents
            progress_callback: Optional callback for progress updates (stage, message)
        """
        self.llm = llm
        self.progress_callback = progress_callback
        
        # Initialize all agents
        log_agent_step(logger, "Orchestrator", "Initializing agents")
        self.paper_analyzer = PaperAnalyzerAgent(llm=llm)
        self.algorithm_designer = AlgorithmDesignerAgent(llm=llm)
        self.code_generator = CodeGeneratorAgent(llm=llm)
        self.code_reviewer = CodeReviewerAgent(llm=llm)
        
        log_success(logger, "All agents initialized")
    
    def convert_paper_to_code(
        self,
        paper_path: str,
        language: str = "python",
        framework: Optional[str] = None,
        include_tests: bool = True,
        include_docs: bool = True,
        output_dir: Optional[str] = None
    ) -> CodeOutput:
        """
        Complete pipeline: Paper → Code
        
        Args:
            paper_path: Path to PDF paper or text file
            language: Target programming language
            framework: Optional framework (e.g., "pytorch")
            include_tests: Generate unit tests
            include_docs: Generate documentation
            output_dir: Directory to save output files (optional)
            
        Returns:
            CodeOutput with generated code
        """
        start_time = time.time()
        
        logger.info("="*60)
        logger.info("Starting Paper-to-Code Conversion Pipeline")
        logger.info("="*60)
        
        try:
            # Stage 1: Load and parse paper
            self._update_progress("parsing", "Loading paper...")
            paper = self._load_paper(paper_path)
            log_success(logger, f"Paper loaded: {paper.metadata.title or 'Untitled'}")
            
            # Stage 2: Analyze paper
            self._update_progress("analyzing", "Analyzing paper methodology...")
            analysis = self.paper_analyzer.analyze_paper(paper)
            log_success(logger, f"Analysis complete: {analysis.algorithm_name}")
            
            # Stage 3: Design implementation
            self._update_progress("designing", "Designing implementation architecture...")
            plan = self.algorithm_designer.design_implementation(
                analysis, language, framework
            )
            log_success(logger, f"Design complete: {len(plan.modules)} modules planned")
            
            # Stage 4: Generate code
            self._update_progress("generating", "Generating code...")
            code_output = self.code_generator.generate_code(
                plan, language, include_tests, include_docs
            )
            log_success(logger, f"Code generated: {code_output.total_lines} lines")
            
            # Stage 5: Review and improve
            self._update_progress("reviewing", "Reviewing and optimizing code...")
            review_result = self.code_reviewer.review_code(code_output)
            log_success(logger, f"Review complete: {review_result.quality_score.value} quality")
            
            # Stage 6: Save output (if directory provided)
            if output_dir:
                self._update_progress("saving", "Saving files...")
                self._save_output(code_output, output_dir)
                log_success(logger, f"Files saved to {output_dir}")
            
            # Complete
            elapsed = time.time() - start_time
            code_output.generation_time = elapsed
            
            logger.info("="*60)
            log_success(logger, f"Pipeline complete in {elapsed:.2f}s")
            logger.info("="*60)
            
            self._update_progress("complete", "Conversion complete!")
            
            return code_output
        
        except Exception as e:
            log_error(logger, f"Pipeline failed: {str(e)}", exc=e)
            self._update_progress("error", f"Error: {str(e)}")
            raise
    
    def _load_paper(self, paper_path: str) -> Paper:
        """Load and parse paper from file"""
        path = Path(paper_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Paper not found: {paper_path}")
        
        # Determine source type
        if path.suffix.lower() == '.pdf':
            # Parse PDF
            parser = PDFParser(str(path))
            parsed = parser.extract_all()
            
            metadata = PaperMetadata(
                title=parsed['metadata'].get('title', ''),
                authors=[parsed['metadata'].get('author', '')] if parsed['metadata'].get('author') else []
            )
            
            paper = Paper(
                source=PaperSource.FILE,
                metadata=metadata,
                full_text=parsed['text'],
                sections=parsed.get('sections', {}),
                file_path=str(path)
            )
        
        elif path.suffix.lower() in ['.txt', '.md']:
            # Plain text
            text = path.read_text(encoding='utf-8')
            
            paper = Paper(
                source=PaperSource.FILE,
                metadata=PaperMetadata(title=path.stem),
                full_text=text,
                file_path=str(path)
            )
        
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        return paper
    
    def _save_output(self, code_output: CodeOutput, output_dir: str):
        """Save generated code to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save code files
        for code_file in code_output.code_files:
            file_path = output_path / code_file.file_name
            file_path.write_text(code_file.code, encoding='utf-8')
            logger.info(f"Saved: {code_file.file_name}")
        
        # Save test files
        for test_file in code_output.test_files:
            file_path = output_path / test_file.file_name
            file_path.write_text(test_file.code, encoding='utf-8')
            logger.info(f"Saved: {test_file.file_name}")
        
        # Save documentation
        if code_output.documentation:
            readme_path = output_path / "README.md"
            readme_path.write_text(code_output.documentation.readme, encoding='utf-8')
            logger.info("Saved: README.md")
            
            # Save requirements
            if code_output.requirements:
                req_path = output_path / "requirements.txt"
                req_path.write_text("\n".join(code_output.requirements), encoding='utf-8')
                logger.info("Saved: requirements.txt")
    
    def _update_progress(self, stage: str, message: str):
        """Update progress via callback if provided"""
        if self.progress_callback:
            self.progress_callback(stage, message)
    
    def convert_from_text(
        self,
        paper_text: str,
        language: str = "python",
        framework: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> CodeOutput:
        """
        Convert algorithm description from text directly
        
        Args:
            paper_text: Algorithm description or paper text
            language: Target programming language
            framework: Optional framework
            output_dir: Output directory
            
        Returns:
            CodeOutput
        """
        logger.info("Converting from text input")
        
        # Create paper object
        paper = Paper(
            source=PaperSource.TEXT,
            metadata=PaperMetadata(title="Text Input"),
            full_text=paper_text
        )
        
        # Run analysis
        analysis = self.paper_analyzer.analyze_paper(paper)
        
        # Design implementation
        plan = self.algorithm_designer.design_implementation(analysis, language, framework)
        
        # Generate code
        code_output = self.code_generator.generate_code(plan, language, True, True)
        
        # Review
        self.code_reviewer.review_code(code_output)
        
        # Save if directory provided
        if output_dir:
            self._save_output(code_output, output_dir)
        
        return code_output
    
    def create_crew(self) -> Crew:
        """
        Create a CrewAI Crew with all agents
        
        Returns:
            Configured Crew instance
        """
        crew = Crew(
            agents=[
                self.paper_analyzer.agent,
                self.algorithm_designer.agent,
                self.code_generator.agent,
                self.code_reviewer.agent
            ],
            tasks=[],  # Tasks are created dynamically
            process=Process.sequential,
            verbose=settings.verbose,
            memory=settings.memory
        )
        
        return crew
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            'initialized': True,
            'agents': {
                'paper_analyzer': self.paper_analyzer is not None,
                'algorithm_designer': self.algorithm_designer is not None,
                'code_generator': self.code_generator is not None,
                'code_reviewer': self.code_reviewer is not None
            },
            'settings': {
                'language': settings.default_language,
                'verbose': settings.verbose,
                'max_iterations': settings.max_iterations
            }
        }


def quick_convert(paper_path: str, output_dir: str, language: str = "python") -> CodeOutput:
    """
    Convenience function for quick conversion
    
    Args:
        paper_path: Path to paper file
        output_dir: Output directory
        language: Programming language
        
    Returns:
        CodeOutput
    """
    orchestrator = Paper2CodeOrchestrator()
    return orchestrator.convert_paper_to_code(
        paper_path=paper_path,
        language=language,
        output_dir=output_dir
    )