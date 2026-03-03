"""Code analyzer agent for static code analysis."""

from typing import Dict, List, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel

from algorithms.ast_analyzer import ASTAnalyzer
from algorithms.complexity_metrics import ComplexityAnalyzer
from algorithms.pattern_detector import PatternDetector
from models.llm_provider import LLMFactory
from utils.logger import AgentLogger
from prompts.analyzer_prompts import ANALYZER_SYSTEM_PROMPT, ANALYZER_USER_PROMPT


class CodeAnalyzerAgent:
    """Agent for comprehensive code analysis."""
    
    def __init__(self, llm: BaseChatModel = None):
        """
        Initialize code analyzer agent.
        
        Args:
            llm: Language model to use (defaults to analyzer LLM)
        """
        self.llm = llm or LLMFactory.create_analyzer_llm()
        self.logger = AgentLogger("CodeAnalyzer")
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Perform comprehensive code analysis.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Analysis results including issues, metrics, and patterns
        """
        self.logger.info("Starting code analysis")
        
        try:
            # Run algorithmic analysis
            ast_results = self._run_ast_analysis(code)
            complexity_results = self._run_complexity_analysis(code)
            pattern_results = self._run_pattern_detection(code)
            
            # Combine results
            combined_results = {
                "ast_analysis": ast_results,
                "complexity_metrics": complexity_results,
                "patterns": pattern_results,
                "summary": self._generate_summary(ast_results, complexity_results, pattern_results)
            }
            
            # Get LLM insights
            llm_insights = self._get_llm_insights(code, combined_results)
            combined_results["llm_insights"] = llm_insights
            
            self.logger.info(f"Analysis complete: {len(ast_results['issues'])} issues found")
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return {
                "error": str(e),
                "ast_analysis": {},
                "complexity_metrics": {},
                "patterns": [],
                "llm_insights": ""
            }
    
    def _run_ast_analysis(self, code: str) -> Dict[str, Any]:
        """Run AST-based analysis."""
        self.logger.debug("Running AST analysis")
        
        try:
            analyzer = ASTAnalyzer(code)
            return analyzer.analyze()
        except Exception as e:
            self.logger.error(f"AST analysis failed: {str(e)}")
            return {"issues": [], "metrics": {}, "error": str(e)}
    
    def _run_complexity_analysis(self, code: str) -> Dict[str, Any]:
        """Run complexity metrics analysis."""
        self.logger.debug("Running complexity analysis")
        
        try:
            analyzer = ComplexityAnalyzer(code)
            return analyzer.analyze_all()
        except Exception as e:
            self.logger.error(f"Complexity analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def _run_pattern_detection(self, code: str) -> List[Any]:
        """Run pattern detection."""
        self.logger.debug("Running pattern detection")
        
        try:
            detector = PatternDetector(code)
            return detector.detect_all()
        except Exception as e:
            self.logger.error(f"Pattern detection failed: {str(e)}")
            return []
    
    def _generate_summary(
        self,
        ast_results: Dict,
        complexity_results: Dict,
        pattern_results: List
    ) -> Dict[str, Any]:
        """Generate analysis summary."""
        issues = ast_results.get("issues", [])
        patterns = pattern_results
        
        # Count by severity
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in issues:
            severity = issue.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        for pattern in patterns:
            severity = pattern.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            "total_issues": len(issues),
            "total_patterns": len(patterns),
            "severity_breakdown": severity_counts,
            "maintainability_index": complexity_results.get("maintainability_index", 0),
            "average_complexity": complexity_results.get("cyclomatic", {}).get("average", 0),
            "needs_attention": severity_counts["critical"] > 0 or severity_counts["high"] > 2
        }
    
    def _get_llm_insights(self, code: str, analysis_results: Dict) -> str:
        """Get insights from LLM about the analysis."""
        self.logger.debug("Getting LLM insights")
        
        try:
            # Prepare context for LLM
            summary = analysis_results["summary"]
            issues = analysis_results["ast_analysis"].get("issues", [])[:5]  # Top 5 issues
            patterns = analysis_results["patterns"][:5]  # Top 5 patterns
            
            user_message = ANALYZER_USER_PROMPT.format(
                code=code[:1000],  # Limit code length
                total_issues=summary["total_issues"],
                critical_issues=summary["severity_breakdown"]["critical"],
                high_issues=summary["severity_breakdown"]["high"],
                maintainability_index=summary["maintainability_index"],
                top_issues=self._format_issues(issues),
                top_patterns=self._format_patterns(patterns)
            )
            
            messages = [
                SystemMessage(content=ANALYZER_SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            self.logger.error(f"LLM insights failed: {str(e)}")
            return "LLM analysis unavailable"
    
    def _format_issues(self, issues: List) -> str:
        """Format issues for LLM prompt."""
        if not issues:
            return "No critical issues found"
        
        formatted = []
        for issue in issues:
            formatted.append(
                f"- Line {issue.line_number}: {issue.category} - {issue.message}"
            )
        return "\n".join(formatted)
    
    def _format_patterns(self, patterns: List) -> str:
        """Format patterns for LLM prompt."""
        if not patterns:
            return "No anti-patterns detected"
        
        formatted = []
        for pattern in patterns:
            formatted.append(
                f"- {pattern.name} (Line {pattern.line_number}): {pattern.description}"
            )
        return "\n".join(formatted)
    
    def get_critical_issues(self, analysis_results: Dict) -> List:
        """Extract critical issues from analysis results."""
        issues = analysis_results.get("ast_analysis", {}).get("issues", [])
        patterns = analysis_results.get("patterns", [])
        
        critical = []
        
        for issue in issues:
            if issue.severity.lower() in ["critical", "high"]:
                critical.append({
                    "type": "issue",
                    "severity": issue.severity,
                    "category": issue.category,
                    "message": issue.message,
                    "line": issue.line_number,
                    "suggestion": issue.suggestion
                })
        
        for pattern in patterns:
            if pattern.severity.lower() in ["critical", "high"]:
                critical.append({
                    "type": "pattern",
                    "severity": pattern.severity,
                    "name": pattern.name,
                    "description": pattern.description,
                    "line": pattern.line_number,
                    "recommendation": pattern.recommendation
                })
        
        return critical