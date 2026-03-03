"""
Paper Analyzer Agent - Extracts methodology from research papers
"""
from crewai import Agent, Task
from typing import Dict, List
from models import Paper, PaperAnalysis
from tools import PDFParser, LatexParser
from config import PAPER_ANALYZER_PROMPT, settings
from utils.logger import logger, log_agent_step
import json


class PaperAnalyzerAgent:
    """Agent responsible for analyzing research papers and extracting algorithmic information"""
    
    def __init__(self, llm=None):
        """
        Initialize Paper Analyzer Agent
        
        Args:
            llm: Language model instance (optional, will use default from settings)
        """
        self.llm = llm
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent"""
        return Agent(
            role="Research Paper Analyzer",
            goal="Extract and understand algorithmic methodologies from research papers",
            backstory="""You are an expert in reading and analyzing academic research papers, 
            particularly in computer science, machine learning, and algorithms. You have a deep 
            understanding of mathematical notation, algorithmic thinking, and can identify key 
            implementation details that others might miss. Your specialty is translating academic 
            concepts into actionable implementation plans.""",
            verbose=settings.verbose,
            allow_delegation=False,
            llm=self.llm
        )
    
    def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """
        Analyze a research paper and extract implementation-relevant information
        
        Args:
            paper: Paper object to analyze
            
        Returns:
            PaperAnalysis with extracted information
        """
        log_agent_step(logger, "Paper Analyzer", "Starting paper analysis")
        
        # Parse LaTeX equations
        latex_parser = LatexParser()
        equations = latex_parser.batch_parse(paper.full_text)
        
        # Create analysis task
        task = Task(
            description=self._create_analysis_prompt(paper, equations),
            agent=self.agent,
            expected_output="""A detailed JSON analysis containing:
            1. Algorithm name and type
            2. Core methodology description
            3. Step-by-step algorithm breakdown
            4. Input/output specifications
            5. Key data structures needed
            6. Mathematical formulations
            7. Complexity analysis
            8. Implementation challenges and edge cases
            9. Required dependencies/prerequisites"""
        )
        
        # Execute analysis using Crew
        log_agent_step(logger, "Paper Analyzer", "Executing analysis task")
        from crewai import Crew, Process
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Extract string from CrewOutput
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        # Parse result into PaperAnalysis
        analysis = self._parse_analysis_result(result_str, paper.id, equations)
        
        log_agent_step(
            logger,
            "Paper Analyzer",
            f"Analysis complete: {analysis.algorithm_name}",
            f"Confidence: {analysis.confidence_score:.2f}"
        )
        
        return analysis
    
    def _create_analysis_prompt(self, paper: Paper, equations: List[Dict]) -> str:
        """Create detailed analysis prompt for the agent"""
        
        # Extract relevant sections
        methodology_sections = []
        for section_name, content in paper.sections.items():
            if any(keyword in section_name.lower() for keyword in 
                   ['method', 'approach', 'algorithm', 'implementation']):
                methodology_sections.append(f"## {section_name}\n{content}")
        
        methodology_text = "\n\n".join(methodology_sections) if methodology_sections else paper.full_text[:5000]
        
        # Format equations
        equations_text = "\n".join([
            f"Equation {i+1}: {eq['latex']}" 
            for i, eq in enumerate(equations[:10])
        ]) if equations else "No equations extracted."
        
        prompt = f"""
{PAPER_ANALYZER_PROMPT}

# PAPER TO ANALYZE

**Title**: {paper.metadata.title or "Unknown"}
**Authors**: {', '.join(paper.metadata.authors) if paper.metadata.authors else "Unknown"}

## Abstract
{paper.metadata.abstract or "No abstract available"}

## Relevant Methodology Sections
{methodology_text}

## Mathematical Formulations
{equations_text}

---

# YOUR TASK

Analyze this paper thoroughly and extract all information needed to implement the algorithm.

Focus on:
1. **Algorithm Identification**: What is the core algorithm? What problem does it solve?
2. **Step-by-Step Breakdown**: Break down the algorithm into clear, implementable steps
3. **Mathematical Foundation**: Identify key equations and their role
4. **Data Structures**: What data structures are needed?
5. **Input/Output**: What are the exact input and output specifications?
6. **Complexity**: Time and space complexity analysis
7. **Edge Cases**: What special cases must be handled?
8. **Dependencies**: What libraries or prerequisites are needed?

Provide your analysis in a structured JSON format with the following keys:
- algorithm_name: string
- algorithm_type: string (e.g., "optimization", "supervised_learning", "graph_algorithm")
- problem_description: string
- algorithm_steps: list of strings (step-by-step breakdown)
- input_specification: string
- output_specification: string
- key_data_structures: list of strings
- mathematical_formulations: list of objects with {{equation, description, variables}}
- complexity_time: string
- complexity_space: string
- edge_cases: list of strings
- dependencies: list of strings
- implementation_challenges: list of strings
- confidence_score: float (0.0-1.0)
- notes: string

Be thorough and precise. If information is unclear, note it in the notes field.
"""
        return prompt
    
    def _parse_analysis_result(self, result: str, paper_id: str, equations: List[Dict]) -> PaperAnalysis:
        """Parse the agent's analysis result into PaperAnalysis object"""
        
        try:
            # Try to parse as JSON
            if '```json' in result:
                json_str = result.split('```json')[1].split('```')[0].strip()
            elif '```' in result:
                json_str = result.split('```')[1].split('```')[0].strip()
            else:
                json_str = result
            
            data = json.loads(json_str)
            
            # Extract complexity
            complexity_analysis = {
                'time': data.get('complexity_time', 'Not specified'),
                'space': data.get('complexity_space', 'Not specified')
            }
            
            # Extract key equations
            key_equations = [eq['latex'] for eq in equations[:5]]
            
            analysis = PaperAnalysis(
                paper_id=paper_id,
                algorithm_name=data.get('algorithm_name', 'Unknown Algorithm'),
                algorithm_type=data.get('algorithm_type', 'unknown'),
                complexity_analysis=complexity_analysis,
                input_specification=data.get('input_specification', ''),
                output_specification=data.get('output_specification', ''),
                prerequisites=data.get('dependencies', []),
                dependencies=data.get('dependencies', []),
                key_data_structures=data.get('key_data_structures', []),
                critical_implementation_details=data.get('implementation_challenges', []),
                edge_cases=data.get('edge_cases', []),
                key_equations=key_equations,
                confidence_score=float(data.get('confidence_score', 0.7)),
                analysis_notes=data.get('notes', '')
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error parsing analysis result: {str(e)}")
            
            # Create fallback analysis
            return PaperAnalysis(
                paper_id=paper_id,
                algorithm_name="Algorithm from paper",
                algorithm_type="unknown",
                input_specification="To be determined",
                output_specification="To be determined",
                confidence_score=0.3,
                analysis_notes=f"Error parsing analysis: {str(e)}\n\nRaw result:\n{result}"
            )
    
    def quick_analyze(self, paper_text: str) -> Dict:
        """
        Quick analysis without full paper object
        
        Args:
            paper_text: Raw text of the paper
            
        Returns:
            Dictionary with basic analysis
        """
        log_agent_step(logger, "Paper Analyzer", "Performing quick analysis")
        
        # Create minimal paper object
        paper = Paper(
            source="text",
            metadata={},
            full_text=paper_text[:10000]  # Limit for quick analysis
        )
        
        analysis = self.analyze_paper(paper)
        
        return {
            'algorithm_name': analysis.algorithm_name,
            'algorithm_type': analysis.algorithm_type,
            'complexity': analysis.complexity_analysis,
            'confidence': analysis.confidence_score
        }