"""
Code Generator Agent - Writes production-ready code
"""
from crewai import Agent, Task
from typing import List
from models import ImplementationPlan, CodeFile, CodeOutput, ProgrammingLanguage, Documentation
from tools import CodeFormatter
from config import CODE_GENERATOR_PROMPT, settings
from utils.logger import logger, log_agent_step
import json


class CodeGeneratorAgent:
    """Agent responsible for generating production-ready code"""
    
    def __init__(self, llm=None):
        """
        Initialize Code Generator Agent
        
        Args:
            llm: Language model instance (optional)
        """
        self.llm = llm
        self.agent = self._create_agent()
        self.formatter = CodeFormatter()
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent"""
        return Agent(
            role="Expert Software Developer",
            goal="Write clean, efficient, and well-documented production-ready code",
            backstory="""You are a world-class software developer with expertise across 
            multiple programming languages. You write code that is not just functional, but 
            elegant, efficient, and maintainable. You follow best practices religiously: 
            proper documentation, type hints, error handling, and clean architecture. Your 
            code is self-explanatory and thoroughly tested. You have implemented countless 
            algorithms from research papers and know how to translate academic concepts into 
            production-quality code.""",
            verbose=settings.verbose,
            allow_delegation=False,
            llm=self.llm
        )
    
    def generate_code(
        self,
        plan: ImplementationPlan,
        language: str = "python",
        include_tests: bool = True,
        include_docs: bool = True
    ) -> CodeOutput:
        """
        Generate complete code implementation from plan
        
        Args:
            plan: ImplementationPlan from Algorithm Designer
            language: Programming language
            include_tests: Whether to generate tests
            include_docs: Whether to generate documentation
            
        Returns:
            CodeOutput with all generated files
        """
        log_agent_step(
            logger,
            "Code Generator",
            f"Generating {language} code from implementation plan"
        )
        
        # Generate code for each module
        code_files = []
        for module in plan.modules:
            log_agent_step(logger, "Code Generator", f"Generating {module.file_name}")
            code_file = self._generate_module(module, plan, language)
            code_files.append(code_file)
        
        # Generate tests if requested
        test_files = []
        if include_tests:
            log_agent_step(logger, "Code Generator", "Generating tests")
            test_files = self._generate_tests(plan, language, code_files)
        
        # Generate documentation if requested
        documentation = None
        if include_docs:
            log_agent_step(logger, "Code Generator", "Generating documentation")
            documentation = self._generate_documentation(plan, code_files)
        
        # Create code output
        output = CodeOutput(
            paper_id=plan.paper_id,
            language=ProgrammingLanguage(language),
            code_files=code_files,
            test_files=test_files,
            documentation=documentation,
            requirements=plan.required_libraries,
            implementation_plan=plan
        )
        
        log_agent_step(
            logger,
            "Code Generator",
            f"Code generation complete: {len(code_files)} files, {output.total_lines} lines"
        )
        
        return output
    
    def _generate_module(
        self,
        module: 'ModuleStructure',
        plan: ImplementationPlan,
        language: str
    ) -> CodeFile:
        """Generate code for a single module"""
        
        # Find relevant function signatures for this module
        relevant_functions = [
            func for func in plan.function_signatures
            if any(export in func.name for export in module.exports)
        ] if module.exports else plan.function_signatures
        
        # Create generation task
        task = Task(
            description=self._create_generation_prompt(
                module, plan, relevant_functions, language
            ),
            agent=self.agent,
            expected_output=f"Complete, production-ready {language} code for {module.file_name}"
        )
        
        # Generate code using Crew
        from crewai import Crew, Process
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Extract string from CrewOutput
        raw_code = result.raw if hasattr(result, 'raw') else str(result)
        
        # Extract code from markdown if present
        code = self._extract_code(raw_code, language)
        
        # Format code
        formatted_code = self.formatter.format(code, language)
        
        return CodeFile(
            file_name=module.file_name,
            file_path=module.file_path,
            language=ProgrammingLanguage(language),
            code=formatted_code,
            description=module.description,
            dependencies=module.dependencies
        )
    
    def _create_generation_prompt(
        self,
        module: 'ModuleStructure',
        plan: ImplementationPlan,
        functions: List['FunctionSignature'],
        language: str
    ) -> str:
        """Create code generation prompt"""
        
        # Format function signatures
        func_specs = []
        for func in functions:
            params = ", ".join([
                f"{p['name']}: {p.get('type', 'Any')}"
                for p in func.parameters
            ])
            func_specs.append(
                f"- {func.name}({params}) -> {func.return_type}\n  {func.description}"
            )
        
        functions_text = "\n".join(func_specs) if func_specs else "Functions to be determined based on module purpose"
        
        # Format data structures
        data_structures_text = "\n".join([
            f"- {name}: {desc}"
            for name, desc in plan.data_structures.items()
        ]) if plan.data_structures else "Standard data structures"
        
        prompt = f"""
{CODE_GENERATOR_PROMPT}

# MODULE TO IMPLEMENT

**File**: {module.file_name}
**Path**: {module.file_path}
**Purpose**: {module.description}
**Language**: {language.upper()}

## Dependencies
{', '.join(module.dependencies) if module.dependencies else 'None'}

## Functions to Implement
{functions_text}

## Data Structures Available
{data_structures_text}

## Implementation Context
{plan.design_rationale[:500] if plan.design_rationale else 'Follow best practices for this language'}

---

# YOUR TASK

Write complete, production-ready {language} code for this module.

**Requirements:**
1. **Complete Implementation**: All functions fully implemented, no placeholders
2. **Documentation**: Comprehensive docstrings/comments for all functions and classes
3. **Type Hints**: Use type hints (Python) or appropriate type declarations
4. **Error Handling**: Proper exception handling and validation
5. **Code Quality**: Follow {language} best practices and style guidelines
6. **Performance**: Implement efficiently considering complexity requirements
7. **Testing-Ready**: Code should be easily testable

**Code Style Guidelines:**
{'- Follow PEP 8' if language == 'python' else '- Follow language conventions'}
- Clear variable and function names
- Avoid magic numbers
- Keep functions focused (single responsibility)
- Add comments for complex logic
- Use meaningful docstrings

**Example Structure** (Python):
```python
\"\"\"
Module description here.
\"\"\"
from typing import List, Dict, Optional
import necessary_libs

def function_name(param1: Type1, param2: Type2) -> ReturnType:
    \"\"\"
    Function description.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this happens
    \"\"\"
    # Implementation here
    pass
```

Now write the complete module code. Return ONLY the code, no explanations.
"""
        return prompt
    
    def _extract_code(self, text: str, language: str) -> str:
        """Extract code from markdown or raw text"""
        # Try to extract from code blocks
        if f'```{language}' in text:
            code = text.split(f'```{language}')[1].split('```')[0].strip()
            return code
        elif '```' in text:
            # Generic code block
            parts = text.split('```')
            if len(parts) >= 3:
                return parts[1].strip()
        
        # Return as-is if no code blocks found
        return text.strip()
    
    def _generate_tests(
        self,
        plan: ImplementationPlan,
        language: str,
        code_files: List[CodeFile]
    ) -> List['TestFile']:
        """Generate test files"""
        from models import TestFile
        
        test_files = []
        
        # Generate test file for main algorithm
        main_file = next(
            (f for f in code_files if f.file_name == plan.main_algorithm_file),
            code_files[0] if code_files else None
        )
        
        if not main_file:
            return []
        
        task = Task(
            description=f"""
Generate comprehensive unit tests for this code module.

**Module**: {main_file.file_name}
**Language**: {language}

**Code to Test**:
```{language}
{main_file.code[:2000]}  # First 2000 chars
```

**Test Cases to Cover**:
{chr(10).join(f"- {tc.get('description', tc.get('name', 'Test case'))}" for tc in plan.test_cases[:5])}

Write complete unit tests using {
    'pytest' if language == 'python' 
    else 'jest' if language in ['javascript', 'typescript']
    else 'standard testing framework'
}.

Include:
- Basic functionality tests
- Edge case tests
- Error handling tests
- Integration tests if applicable

Return ONLY the test code.
""",
            agent=self.agent,
            expected_output=f"Complete unit tests in {language}"
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
        test_code = self._extract_code(result_str, language)
        
        test_file = TestFile(
            file_name=f"test_{main_file.file_name}",
            file_path=main_file.file_path,
            language=ProgrammingLanguage(language),
            code=test_code,
            test_count=test_code.count('def test_') if language == 'python' else test_code.count('test(')
        )
        
        test_files.append(test_file)
        
        return test_files
    
    def _generate_documentation(
        self,
        plan: ImplementationPlan,
        code_files: List[CodeFile]
    ) -> Documentation:
        """Generate README and usage documentation"""
        
        task = Task(
            description=f"""
Generate comprehensive documentation for this implementation.

**Algorithm**: Based on implementation plan
**Files Generated**: {', '.join(f.file_name for f in code_files)}
**Dependencies**: {', '.join(plan.required_libraries)}

Create a README.md that includes:

1. **Overview**: What this implements
2. **Installation**: How to install dependencies
3. **Usage**: Code examples showing how to use
4. **API Documentation**: Key functions and their parameters
5. **Examples**: At least 2 usage examples
6. **Performance**: Expected complexity and performance notes
7. **Contributing**: Basic contribution guidelines
8. **License**: MIT license template

Write in clear, professional markdown. Include code examples.
""",
            agent=self.agent,
            expected_output="Complete README.md in markdown format"
        )
        
        from crewai import Crew, Process
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Extract string from CrewOutput
        readme = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        # Extract usage examples from README
        usage_examples = []
        if '```' in readme:
            examples = readme.split('```')
            for i in range(1, len(examples), 2):
                usage_examples.append(examples[i].strip())
        
        return Documentation(
            readme=readme,
            usage_examples=usage_examples[:3],
            installation_instructions="\n".join(plan.required_libraries)
        )


def generate_simple_code(algorithm_description: str, language: str = "python") -> str:
    """
    Quick code generation without full pipeline
    
    Args:
        algorithm_description: Description of algorithm to implement
        language: Programming language
        
    Returns:
        Generated code string
    """
    agent = CodeGeneratorAgent()
    
    task = Task(
        description=f"""
Implement the following algorithm in {language}:

{algorithm_description}

Provide complete, working code with documentation.
""",
        agent=agent.agent,
        expected_output=f"Complete {language} code"
    )
    
    from crewai import Crew, Process
    
    crew = Crew(
        agents=[agent.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )
    
    result = crew.kickoff()
    result_str = result.raw if hasattr(result, 'raw') else str(result)
    return agent._extract_code(result_str, language)