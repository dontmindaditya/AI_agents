"""
Code Reviewer Agent - Reviews, validates, and optimizes code
"""
from crewai import Agent, Task
from typing import List, Dict
from models import CodeOutput, CodeReviewResult, CodeQuality, TestFile
from tools import CodeValidator, CodeFormatter
from config import CODE_REVIEWER_PROMPT, settings
from utils.logger import logger, log_agent_step
import json


class CodeReviewerAgent:
    """Agent responsible for reviewing and improving generated code"""
    
    def __init__(self, llm=None):
        """
        Initialize Code Reviewer Agent
        
        Args:
            llm: Language model instance (optional)
        """
        self.llm = llm
        self.agent = self._create_agent()
        self.validator = CodeValidator()
        self.formatter = CodeFormatter()
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent"""
        return Agent(
            role="Senior Code Reviewer & QA Specialist",
            goal="Ensure code correctness, quality, and optimal performance",
            backstory="""You are a meticulous code reviewer with years of experience in 
            quality assurance and performance optimization. You have an eye for bugs that 
            others miss and can spot potential issues before they become problems. You 
            understand algorithmic complexity deeply and can suggest concrete optimizations. 
            You believe in rigorous testing and comprehensive error handling. Your reviews 
            are thorough but constructive, focusing on making code better while maintaining 
            functionality. You've reviewed implementations of countless research papers and 
            know the common pitfalls.""",
            verbose=settings.verbose,
            allow_delegation=False,
            llm=self.llm
        )
    
    def review_code(self, code_output: CodeOutput) -> CodeReviewResult:
        """
        Review and improve generated code
        
        Args:
            code_output: CodeOutput from Code Generator
            
        Returns:
            CodeReviewResult with findings and improvements
        """
        log_agent_step(
            logger,
            "Code Reviewer",
            f"Reviewing {len(code_output.code_files)} code files"
        )
        
        # Validate all code files
        validation_results = []
        for code_file in code_output.code_files:
            result = self.validator.validate(code_file.code, code_file.language.value)
            validation_results.append((code_file.file_name, result))
            
            if not result['valid']:
                log_agent_step(
                    logger,
                    "Code Reviewer",
                    f"Validation issues in {code_file.file_name}",
                    f"Errors: {len(result['errors'])}, Warnings: {len(result['warnings'])}"
                )
        
        # Perform comprehensive review
        review_result = self._perform_review(code_output, validation_results)
        
        # Apply fixes and improvements
        improved_output = self._apply_improvements(code_output, review_result)
        
        # Update code output
        code_output.code_files = improved_output.code_files
        code_output.test_files = improved_output.test_files
        code_output.is_validated = True
        code_output.review_result = review_result
        
        log_agent_step(
            logger,
            "Code Reviewer",
            f"Review complete: {review_result.quality_score.value} quality",
            f"Bugs fixed: {len(review_result.fixes_applied)}, Tests added: {len(improved_output.test_files)}"
        )
        
        return review_result
    
    def _perform_review(
        self,
        code_output: CodeOutput,
        validation_results: List[tuple]
    ) -> CodeReviewResult:
        """Perform comprehensive code review"""
        
        # Compile all code for review
        all_code = "\n\n# " + "="*50 + "\n\n".join([
            f"# FILE: {f.file_name}\n{f.code}"
            for f in code_output.code_files
        ])
        
        # Compile validation issues
        validation_summary = []
        for file_name, result in validation_results:
            if result['errors']:
                validation_summary.append(f"**{file_name}**: {len(result['errors'])} errors")
            if result['warnings']:
                validation_summary.append(f"**{file_name}**: {len(result['warnings'])} warnings")
        
        validation_text = "\n".join(validation_summary) if validation_summary else "No validation errors"
        
        # Create review task
        task = Task(
            description=self._create_review_prompt(
                code_output, all_code[:5000], validation_text
            ),
            agent=self.agent,
            expected_output="""A comprehensive review in JSON format with:
            1. List of bugs found (location, description, severity)
            2. Suggested optimizations (location, suggestion, impact)
            3. Style issues found
            4. Correctness verification
            5. Performance analysis
            6. Quality score (excellent/good/fair/needs_improvement)
            7. List of improvements to make
            8. Additional test cases needed"""
        )
        
        # Execute review using Crew
        from crewai import Crew, Process
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        # Parse review result
        review = self._parse_review_result(result_str, validation_results)
        
        return review
    
    def _create_review_prompt(
        self,
        code_output: CodeOutput,
        code_sample: str,
        validation_summary: str
    ) -> str:
        """Create comprehensive review prompt"""
        
        prompt = f"""
{CODE_REVIEWER_PROMPT}

# CODE TO REVIEW

**Language**: {code_output.language.value}
**Files**: {len(code_output.code_files)} code files, {len(code_output.test_files)} test files
**Total Lines**: {code_output.total_lines}
**Framework**: {code_output.framework or 'Standard library'}

## Validation Results
{validation_summary}

## Code Sample (first 5000 chars)
```{code_output.language.value}
{code_sample}
```

## Original Implementation Plan Summary
{code_output.implementation_plan.design_rationale[:300] if code_output.implementation_plan else 'Not available'}

---

# YOUR REVIEW TASK

Perform a thorough code review focusing on:

## 1. CORRECTNESS
- Does the code correctly implement the algorithm?
- Are there any logical errors or bugs?
- Are edge cases handled properly?
- Is error handling appropriate?

## 2. PERFORMANCE
- Are there any obvious performance issues?
- Can any algorithms be optimized?
- Are data structures used efficiently?
- Any unnecessary computations?

## 3. CODE QUALITY
- Is the code readable and maintainable?
- Are naming conventions followed?
- Is the code properly documented?
- Are there any code smells?
- Is complexity manageable?

## 4. TESTING
- Are the tests comprehensive?
- Are edge cases tested?
- Is error handling tested?
- Any missing test scenarios?

## 5. SECURITY & BEST PRACTICES
- Any security vulnerabilities?
- Are best practices followed?
- Proper input validation?
- Resource management (memory, files, etc.)?

Provide your review as JSON with these keys:

```json
{{
  "bugs_found": [
    {{"location": "file:line", "description": "...", "severity": "high|medium|low"}}
  ],
  "optimizations": [
    {{"location": "file:line", "suggestion": "...", "impact": "high|medium|low"}}
  ],
  "style_issues": ["issue1", "issue2"],
  "correctness_verification": "Overall assessment of correctness",
  "performance_analysis": "Performance assessment and bottlenecks",
  "quality_score": "excellent|good|fair|needs_improvement",
  "improvements_needed": ["improvement1", "improvement2"],
  "additional_tests": [
    {{"name": "test_name", "description": "...", "test_code": "..."}}
  ]
}}
```

Be thorough but constructive. Focus on making the code better.
"""
        return prompt
    
    def _parse_review_result(
        self,
        result: str,
        validation_results: List[tuple]
    ) -> CodeReviewResult:
        """Parse review result into CodeReviewResult object"""
        
        try:
            # Extract JSON
            if '```json' in result:
                json_str = result.split('```json')[1].split('```')[0].strip()
            elif '```' in result:
                json_str = result.split('```')[1].split('```')[0].strip()
            else:
                json_str = result
            
            data = json.loads(json_str)
            
            # Map quality score
            quality_map = {
                'excellent': CodeQuality.EXCELLENT,
                'good': CodeQuality.GOOD,
                'fair': CodeQuality.FAIR,
                'needs_improvement': CodeQuality.NEEDS_IMPROVEMENT
            }
            
            quality_score = quality_map.get(
                data.get('quality_score', 'good').lower(),
                CodeQuality.GOOD
            )
            
            review = CodeReviewResult(
                bugs_found=data.get('bugs_found', []),
                optimizations=data.get('optimizations', []),
                style_issues=data.get('style_issues', []),
                quality_score=quality_score,
                correctness_verification=data.get('correctness_verification', ''),
                performance_analysis=data.get('performance_analysis', ''),
                fixes_applied=[],  # Will be populated by _apply_improvements
                refactorings=[]
            )
            
            return review
        
        except Exception as e:
            logger.error(f"Error parsing review result: {str(e)}")
            
            # Create fallback review
            return CodeReviewResult(
                quality_score=CodeQuality.FAIR,
                correctness_verification="Review parsing failed - manual review recommended",
                performance_analysis="Unable to analyze - see raw review",
                bugs_found=[],
                optimizations=[]
            )
    
    def _apply_improvements(
        self,
        code_output: CodeOutput,
        review: CodeReviewResult
    ) -> CodeOutput:
        """Apply improvements based on review"""
        
        log_agent_step(logger, "Code Reviewer", "Applying improvements")
        
        improved_files = []
        
        # Fix critical bugs in each file
        for code_file in code_output.code_files:
            # Check if this file has bugs
            file_bugs = [
                bug for bug in review.bugs_found
                if code_file.file_name in bug.get('location', '')
            ]
            
            if file_bugs and len(file_bugs) <= 3:  # Only auto-fix if few bugs
                improved_code = self._fix_bugs(code_file.code, file_bugs, code_output.language.value)
                code_file.code = improved_code
                
                for bug in file_bugs:
                    review.fixes_applied.append(f"Fixed: {bug['description']}")
            
            # Format code
            code_file.code = self.formatter.format(code_file.code, code_output.language.value)
            
            improved_files.append(code_file)
        
        code_output.code_files = improved_files
        
        # Generate additional tests if needed
        if len(code_output.test_files) == 0:
            log_agent_step(logger, "Code Reviewer", "Generating missing tests")
            # This would ideally call code generator, but for now we note it
            review.edge_cases_covered.append("Note: Tests should be added")
        
        return code_output
    
    def _fix_bugs(self, code: str, bugs: List[Dict], language: str) -> str:
        """Attempt to automatically fix bugs"""
        
        # For simple fixes only
        # In production, this would be more sophisticated
        
        task = Task(
            description=f"""
Fix the following bugs in this code:

**Bugs to Fix**:
{chr(10).join(f"- {bug['description']} (at {bug.get('location', 'unknown')})" for bug in bugs)}

**Code**:
```{language}
{code}
```

Return the fixed code. Make minimal changes - only fix the specific bugs mentioned.
""",
            agent=self.agent,
            expected_output=f"Fixed {language} code"
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
        
        # Extract code
        if f'```{language}' in result_str:
            fixed_code = result_str.split(f'```{language}')[1].split('```')[0].strip()
            return fixed_code
        elif '```' in result_str:
            parts = result_str.split('```')
            if len(parts) >= 3:
                return parts[1].strip()
        
        return code  # Return original if extraction fails
    
    def quick_review(self, code: str, language: str = "python") -> Dict:
        """
        Quick review without full pipeline
        
        Args:
            code: Code string to review
            language: Programming language
            
        Returns:
            Dictionary with review summary
        """
        # Validate
        validation = self.validator.validate(code, language)
        
        # Estimate quality
        quality_score = self.validator.estimate_quality_score(code, language)
        
        return {
            'valid': validation['valid'],
            'errors': len(validation.get('errors', [])),
            'warnings': len(validation.get('warnings', [])),
            'quality_score': quality_score,
            'issues': validation.get('errors', []) + validation.get('warnings', [])
        }