"""Optimization suggester agent for generating optimization recommendations."""

from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel

from algorithms.optimization_ranker import OptimizationRanker, ImpactLevel, EffortLevel
from models.llm_provider import LLMFactory
from utils.logger import AgentLogger
from prompts.optimizer_prompts import OPTIMIZER_SYSTEM_PROMPT, OPTIMIZER_USER_PROMPT


class OptimizationSuggesterAgent:
    """Agent for generating and ranking optimization suggestions."""
    
    def __init__(self, llm: BaseChatModel = None):
        """
        Initialize optimization suggester agent.
        
        Args:
            llm: Language model to use
        """
        self.llm = llm or LLMFactory.create_optimizer_llm()
        self.logger = AgentLogger("OptimizationSuggester")
    
    def suggest(
        self,
        code: str,
        analysis_results: Dict[str, Any],
        performance_results: Dict[str, Any],
        memory_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimization suggestions based on analysis results.
        
        Args:
            code: Original code
            analysis_results: Code analysis results
            performance_results: Performance analysis results
            memory_results: Memory analysis results
            
        Returns:
            Optimization suggestions and implementation plan
        """
        self.logger.info("Generating optimization suggestions")
        
        try:
            # Create optimization ranker from analysis results
            ranker = self._create_ranker(
                analysis_results,
                performance_results,
                memory_results
            )
            
            # Get ranked opportunities
            opportunities = ranker.rank_opportunities()
            quick_wins = ranker.get_quick_wins()
            critical = ranker.get_critical_optimizations()
            
            # Generate implementation plan
            implementation_plan = ranker.generate_implementation_plan()
            
            # Get LLM-generated optimizations
            llm_suggestions = self._get_llm_suggestions(
                code,
                opportunities[:5]  # Top 5
            )
            
            results = {
                "total_opportunities": len(opportunities),
                "quick_wins": [self._format_opportunity(o) for o in quick_wins],
                "critical_optimizations": [self._format_opportunity(o) for o in critical],
                "all_opportunities": [self._format_opportunity(o) for o in opportunities],
                "implementation_plan": self._format_implementation_plan(implementation_plan),
                "llm_suggestions": llm_suggestions,
                "report": ranker.generate_optimization_report()
            }
            
            self.logger.info(f"Generated {len(opportunities)} optimization suggestions")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Optimization suggestion failed: {str(e)}")
            return {
                "error": str(e),
                "total_opportunities": 0,
                "quick_wins": [],
                "critical_optimizations": [],
                "all_opportunities": [],
                "llm_suggestions": ""
            }
    
    def _create_ranker(
        self,
        analysis_results: Dict,
        performance_results: Dict,
        memory_results: Dict
    ) -> OptimizationRanker:
        """Create optimization ranker from all analysis results."""
        self.logger.debug("Creating optimization ranker")
        
        ranker = OptimizationRanker()
        
        # Add code quality issues
        issues = analysis_results.get("ast_analysis", {}).get("issues", [])
        for issue in issues:
            impact = self._severity_to_impact(issue.severity)
            effort = EffortLevel.EASY if impact.value <= 2 else EffortLevel.MODERATE
            
            ranker.add_opportunity(
                title=f"Fix {issue.category}: {issue.message}",
                description=issue.message,
                category="code_quality",
                impact=impact,
                effort=effort,
                line_number=issue.line_number,
                estimated_improvement="Improves code maintainability",
                implementation_steps=[issue.suggestion],
                risks=[]
            )
        
        # Add performance bottlenecks
        bottlenecks = performance_results.get("bottlenecks", [])
        for bottleneck in bottlenecks:
            impact = self._severity_to_impact(bottleneck.severity)
            effort = EffortLevel.MODERATE if impact == ImpactLevel.CRITICAL else EffortLevel.EASY
            
            ranker.add_opportunity(
                title=f"Optimize {bottleneck.type}",
                description=bottleneck.description,
                category="performance",
                impact=impact,
                effort=effort,
                line_number=bottleneck.line_number,
                estimated_improvement=bottleneck.estimated_improvement,
                implementation_steps=[bottleneck.optimization_suggestion],
                risks=["May require algorithm restructuring"]
            )
        
        # Add memory issues
        memory_issues = memory_results.get("static_analysis", [])
        for issue in memory_issues:
            impact = self._severity_to_impact(issue.get("severity", "low"))
            effort = EffortLevel.EASY
            
            ranker.add_opportunity(
                title=f"Fix memory issue: {issue.get('type', 'unknown')}",
                description=issue.get("description", ""),
                category="memory",
                impact=impact,
                effort=effort,
                line_number=issue.get("line", 0),
                estimated_improvement="Reduces memory usage",
                implementation_steps=[issue.get("suggestion", "")],
                risks=[]
            )
        
        return ranker
    
    def _severity_to_impact(self, severity: str) -> ImpactLevel:
        """Convert severity string to ImpactLevel."""
        severity_map = {
            "critical": ImpactLevel.CRITICAL,
            "high": ImpactLevel.HIGH,
            "medium": ImpactLevel.MEDIUM,
            "low": ImpactLevel.LOW
        }
        return severity_map.get(severity.lower(), ImpactLevel.LOW)
    
    def _get_llm_suggestions(self, code: str, top_opportunities: List) -> str:
        """Get LLM-generated optimization suggestions."""
        self.logger.debug("Getting LLM optimization suggestions")
        
        try:
            opportunities_text = self._format_opportunities_for_prompt(top_opportunities)
            
            user_message = OPTIMIZER_USER_PROMPT.format(
                code=code[:2000],  # Limit code length
                opportunities=opportunities_text
            )
            
            messages = [
                SystemMessage(content=OPTIMIZER_SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            self.logger.error(f"LLM suggestions failed: {str(e)}")
            return "LLM suggestions unavailable"
    
    def _format_opportunities_for_prompt(self, opportunities: List) -> str:
        """Format opportunities for LLM prompt."""
        if not opportunities:
            return "No optimization opportunities identified"
        
        formatted = []
        for i, opp in enumerate(opportunities, 1):
            formatted.append(
                f"{i}. {opp.title} (Line {opp.line_number})\n"
                f"   Impact: {opp.impact.name}, Effort: {opp.effort.name}\n"
                f"   Description: {opp.description}\n"
                f"   Improvement: {opp.estimated_improvement}"
            )
        return "\n\n".join(formatted)
    
    def _format_opportunity(self, opp) -> Dict:
        """Format opportunity for output."""
        return {
            "title": opp.title,
            "description": opp.description,
            "category": opp.category,
            "impact": opp.impact.name,
            "effort": opp.effort.name,
            "priority_score": round(opp.priority_score, 2),
            "line_number": opp.line_number,
            "estimated_improvement": opp.estimated_improvement,
            "implementation_steps": opp.implementation_steps,
            "risks": opp.risks
        }
    
    def _format_implementation_plan(self, plan: Dict) -> Dict:
        """Format implementation plan for output."""
        formatted = {}
        for phase, opportunities in plan.items():
            formatted[phase] = [
                self._format_opportunity(opp) for opp in opportunities
            ]
        return formatted
    
    def get_quick_win_recommendations(self, suggestions: Dict) -> List[Dict]:
        """Extract quick win recommendations."""
        return suggestions.get("quick_wins", [])[:5]
    
    def get_critical_recommendations(self, suggestions: Dict) -> List[Dict]:
        """Extract critical recommendations."""
        return suggestions.get("critical_optimizations", [])[:5]