"""
Algorithm Designer Agent - Plans implementation strategy
"""
from crewai import Agent, Task
from typing import Dict, Optional
from models import PaperAnalysis, ImplementationPlan, ModuleStructure, FunctionSignature
from config import ALGORITHM_DESIGNER_PROMPT, settings
from utils.logger import logger, log_agent_step
import json


class AlgorithmDesignerAgent:
    """Agent responsible for designing implementation architecture and strategy"""
    
    def __init__(self, llm=None):
        """
        Initialize Algorithm Designer Agent
        
        Args:
            llm: Language model instance (optional)
        """
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent"""
        return Agent(
            role="Software Architecture Designer",
            goal="Design clean, modular, and efficient implementation plans for algorithms",
            backstory="""You are a senior software architect with deep expertise in algorithm 
            implementation, software design patterns, and clean code principles. You excel at 
            translating complex algorithmic concepts into well-structured, maintainable code 
            architectures. You understand data structures deeply and know how to optimize for 
            both performance and readability. Your designs are always modular, testable, and 
            follow industry best practices.""",
            verbose=settings.verbose,
            allow_delegation=False,
            llm=self.llm
        )
    
    def design_implementation(
        self,
        analysis: PaperAnalysis,
        language: str = "python",
        framework: Optional[str] = None
    ) -> ImplementationPlan:
        """
        Design implementation plan based on paper analysis
        
        Args:
            analysis: PaperAnalysis from Paper Analyzer
            language: Target programming language
            framework: Optional framework (e.g., "pytorch", "tensorflow")
            
        Returns:
            ImplementationPlan with detailed design
        """
        log_agent_step(
            logger,
            "Algorithm Designer",
            f"Designing implementation for {analysis.algorithm_name}"
        )
        
        # Create design task
        task = Task(
            description=self._create_design_prompt(analysis, language, framework),
            agent=self.agent,
            expected_output="""A comprehensive implementation plan in JSON format containing:
            1. Module/file structure with descriptions
            2. Function signatures with parameters and return types
            3. Data structure designs
            4. Class hierarchy (if applicable)
            5. Implementation steps in order
            6. Required libraries and dependencies
            7. Test case designs
            8. Performance optimization opportunities
            9. Potential implementation challenges"""
        )
        
        # Execute design using Crew
        log_agent_step(logger, "Algorithm Designer", "Creating implementation design")
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
        
        # Parse result
        plan = self._parse_design_result(result_str, analysis.paper_id, language)
        
        log_agent_step(
            logger,
            "Algorithm Designer",
            f"Design complete: {len(plan.modules)} modules, {len(plan.function_signatures)} functions"
        )
        
        return plan
    
    def _create_design_prompt(
        self,
        analysis: PaperAnalysis,
        language: str,
        framework: Optional[str]
    ) -> str:
        """Create detailed design prompt"""
        
        framework_text = f"using the {framework} framework" if framework else ""
        
        prompt = f"""
{ALGORITHM_DESIGNER_PROMPT}

# ALGORITHM ANALYSIS

**Algorithm**: {analysis.algorithm_name}
**Type**: {analysis.algorithm_type}

## Problem & Solution
{analysis.analysis_notes[:500] if analysis.analysis_notes else "See specifications below"}

## Input Specification
{analysis.input_specification}

## Output Specification
{analysis.output_specification}

## Required Data Structures
{', '.join(analysis.key_data_structures) if analysis.key_data_structures else 'To be determined'}

## Complexity Requirements
- Time Complexity: {analysis.complexity_analysis.get('time', 'Unknown')}
- Space Complexity: {analysis.complexity_analysis.get('space', 'Unknown')}

## Edge Cases to Handle
{chr(10).join(f'- {case}' for case in analysis.edge_cases) if analysis.edge_cases else '- Standard error handling'}

## Dependencies Needed
{', '.join(analysis.dependencies) if analysis.dependencies else 'Standard library'}

---

# YOUR TASK

Design a complete, production-ready implementation architecture for this algorithm in **{language.upper()}** {framework_text}.

Your design should include:

## 1. MODULE STRUCTURE
Break the implementation into logical modules/files:
- Main algorithm file
- Helper/utility modules
- Data structure implementations
- Testing module

For each module, specify:
- File name and path
- Purpose and responsibilities
- Dependencies on other modules
- What it exports

## 2. FUNCTION SIGNATURES
Design all key functions with:
- Function name
- Parameters (name, type, description)
- Return type
- Brief description
- Estimated complexity

## 3. DATA STRUCTURES
Design or specify data structures needed:
- Custom classes/structs
- Data formats
- Internal representations

## 4. IMPLEMENTATION STRATEGY
Provide step-by-step implementation plan:
1. What to implement first (foundational pieces)
2. Core algorithm implementation
3. Integration and testing
4. Optimization passes

## 5. TESTING APPROACH
Design test cases covering:
- Basic functionality
- Edge cases
- Performance tests
- Integration tests

## 6. OPTIMIZATION OPPORTUNITIES
Identify potential optimizations:
- Algorithmic improvements
- Memory optimizations
- Caching strategies

Provide your design as a JSON object with these keys:
- modules: list of {{file_name, file_path, description, dependencies, exports}}
- main_algorithm_file: string
- function_signatures: list of {{name, parameters, return_type, description, complexity}}
- data_structures: object with {{name: description}}
- class_hierarchy: string (textual description)
- implementation_steps: list of strings
- required_libraries: list of strings
- test_cases: list of {{name, description, input, expected_output}}
- testing_approach: string
- design_rationale: string
- optimization_opportunities: list of strings
- potential_challenges: list of strings

Focus on clean architecture, modularity, and maintainability.
"""
        return prompt
    
    def _parse_design_result(
        self,
        result: str,
        paper_id: str,
        language: str
    ) -> ImplementationPlan:
        """Parse design result into ImplementationPlan"""
        
        try:
            # Extract JSON
            if '```json' in result:
                json_str = result.split('```json')[1].split('```')[0].strip()
            elif '```' in result:
                json_str = result.split('```')[1].split('```')[0].strip()
            else:
                json_str = result
            
            data = json.loads(json_str)
            
            # Parse modules
            modules = []
            for mod in data.get('modules', []):
                modules.append(ModuleStructure(
                    file_name=mod.get('file_name', 'module.py'),
                    file_path=mod.get('file_path', './'),
                    description=mod.get('description', ''),
                    dependencies=mod.get('dependencies', []),
                    exports=mod.get('exports', [])
                ))
            
            # Parse function signatures
            function_signatures = []
            for func in data.get('function_signatures', []):
                function_signatures.append(FunctionSignature(
                    name=func.get('name', 'function'),
                    parameters=func.get('parameters', []),
                    return_type=func.get('return_type', 'Any'),
                    description=func.get('description', ''),
                    complexity=func.get('complexity')
                ))
            
            # Create implementation plan
            plan = ImplementationPlan(
                paper_id=paper_id,
                modules=modules,
                main_algorithm_file=data.get('main_algorithm_file', 'algorithm.py'),
                function_signatures=function_signatures,
                data_structures=data.get('data_structures', {}),
                class_hierarchy=data.get('class_hierarchy'),
                implementation_steps=data.get('implementation_steps', []),
                required_libraries=data.get('required_libraries', []),
                test_cases=data.get('test_cases', []),
                testing_approach=data.get('testing_approach', ''),
                design_rationale=data.get('design_rationale', ''),
                optimization_opportunities=data.get('optimization_opportunities', []),
                potential_challenges=data.get('potential_challenges', [])
            )
            
            return plan
        
        except Exception as e:
            logger.error(f"Error parsing design result: {str(e)}")
            
            # Create fallback plan
            return ImplementationPlan(
                paper_id=paper_id,
                modules=[ModuleStructure(
                    file_name=f"algorithm.{language}",
                    file_path="./",
                    description="Main algorithm implementation",
                    dependencies=[],
                    exports=["main_algorithm"]
                )],
                main_algorithm_file=f"algorithm.{language}",
                function_signatures=[],
                implementation_steps=[
                    "Set up project structure",
                    "Implement core algorithm",
                    "Add error handling",
                    "Write tests",
                    "Optimize performance"
                ],
                design_rationale=f"Fallback design due to parsing error: {str(e)}\n\nRaw result:\n{result[:500]}"
            )
    
    def refine_design(self, plan: ImplementationPlan, feedback: str) -> ImplementationPlan:
        """
        Refine implementation plan based on feedback
        
        Args:
            plan: Current implementation plan
            feedback: Feedback or requirements to address
            
        Returns:
            Refined ImplementationPlan
        """
        log_agent_step(logger, "Algorithm Designer", "Refining design based on feedback")
        
        task = Task(
            description=f"""
Review and refine this implementation plan based on the feedback provided.

**Current Plan Summary:**
- Modules: {len(plan.modules)}
- Functions: {len(plan.function_signatures)}
- Main file: {plan.main_algorithm_file}

**Feedback to Address:**
{feedback}

Provide an updated design that addresses the feedback while maintaining clean architecture.
Return the complete updated plan in the same JSON format as before.
""",
            agent=self.agent,
            expected_output="Refined implementation plan in JSON format"
        )
        
        from crewai import Crew, Process
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        refined_plan = self._parse_design_result(result_str, plan.paper_id, "python")
        
        return refined_plan