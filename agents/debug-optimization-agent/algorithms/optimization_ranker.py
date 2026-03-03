"""Rank and prioritize optimization opportunities."""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class ImpactLevel(Enum):
    """Impact level of optimization."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


class EffortLevel(Enum):
    """Effort required for optimization."""
    TRIVIAL = 1
    EASY = 2
    MODERATE = 3
    HARD = 4
    VERY_HARD = 5


@dataclass
class OptimizationOpportunity:
    """Represents an optimization opportunity."""
    title: str
    description: str
    category: str
    impact: ImpactLevel
    effort: EffortLevel
    priority_score: float
    line_number: int
    estimated_improvement: str
    implementation_steps: List[str]
    code_before: str
    code_after: str
    risks: List[str]


class OptimizationRanker:
    """Rank and prioritize optimization opportunities."""
    
    def __init__(self):
        """Initialize optimization ranker."""
        self.opportunities: List[OptimizationOpportunity] = []
    
    def add_opportunity(
        self,
        title: str,
        description: str,
        category: str,
        impact: ImpactLevel,
        effort: EffortLevel,
        line_number: int,
        estimated_improvement: str,
        implementation_steps: List[str],
        code_before: str = "",
        code_after: str = "",
        risks: List[str] = None
    ):
        """
        Add an optimization opportunity.
        
        Args:
            title: Short title of optimization
            description: Detailed description
            category: Category (performance, memory, readability, etc.)
            impact: Expected impact level
            effort: Required effort level
            line_number: Line number in code
            estimated_improvement: Expected improvement description
            implementation_steps: Step-by-step implementation guide
            code_before: Current code snippet
            code_after: Optimized code snippet
            risks: Potential risks or considerations
        """
        priority_score = self._calculate_priority(impact, effort)
        
        opportunity = OptimizationOpportunity(
            title=title,
            description=description,
            category=category,
            impact=impact,
            effort=effort,
            priority_score=priority_score,
            line_number=line_number,
            estimated_improvement=estimated_improvement,
            implementation_steps=implementation_steps,
            code_before=code_before,
            code_after=code_after,
            risks=risks or []
        )
        
        self.opportunities.append(opportunity)
    
    def rank_opportunities(self) -> List[OptimizationOpportunity]:
        """
        Rank all opportunities by priority.
        
        Returns:
            Sorted list of optimization opportunities
        """
        return sorted(
            self.opportunities,
            key=lambda x: (x.priority_score, x.impact.value),
            reverse=True
        )
    
    def get_quick_wins(self, max_effort: EffortLevel = EffortLevel.EASY) -> List[OptimizationOpportunity]:
        """
        Get quick wins (high impact, low effort).
        
        Args:
            max_effort: Maximum effort level to consider
            
        Returns:
            List of quick win opportunities
        """
        return [
            opp for opp in self.rank_opportunities()
            if opp.effort.value <= max_effort.value and opp.impact.value >= ImpactLevel.MEDIUM.value
        ]
    
    def get_by_category(self, category: str) -> List[OptimizationOpportunity]:
        """
        Get opportunities by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            Filtered list of opportunities
        """
        return [
            opp for opp in self.rank_opportunities()
            if opp.category == category
        ]
    
    def get_critical_optimizations(self) -> List[OptimizationOpportunity]:
        """
        Get critical optimizations that should be addressed first.
        
        Returns:
            List of critical opportunities
        """
        return [
            opp for opp in self.rank_opportunities()
            if opp.impact == ImpactLevel.CRITICAL
        ]
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report.
        
        Returns:
            Dictionary with optimization analysis
        """
        opportunities = self.rank_opportunities()
        
        if not opportunities:
            return {
                "total_opportunities": 0,
                "message": "No optimization opportunities found"
            }
        
        # Calculate statistics
        impact_distribution = self._count_by_attribute('impact', opportunities)
        effort_distribution = self._count_by_attribute('effort', opportunities)
        category_distribution = self._count_by_attribute('category', opportunities)
        
        quick_wins = self.get_quick_wins()
        critical = self.get_critical_optimizations()
        
        return {
            "total_opportunities": len(opportunities),
            "quick_wins": len(quick_wins),
            "critical_optimizations": len(critical),
            "impact_distribution": impact_distribution,
            "effort_distribution": effort_distribution,
            "category_distribution": category_distribution,
            "top_priorities": [
                {
                    "title": opp.title,
                    "category": opp.category,
                    "impact": opp.impact.name,
                    "effort": opp.effort.name,
                    "priority_score": round(opp.priority_score, 2),
                    "line": opp.line_number
                }
                for opp in opportunities[:10]
            ],
            "quick_wins_list": [
                {
                    "title": opp.title,
                    "estimated_improvement": opp.estimated_improvement,
                    "line": opp.line_number
                }
                for opp in quick_wins[:5]
            ]
        }
    
    def generate_implementation_plan(self) -> Dict[str, List[OptimizationOpportunity]]:
        """
        Generate phased implementation plan.
        
        Returns:
            Dictionary with phases and opportunities
        """
        opportunities = self.rank_opportunities()
        
        # Phase 1: Quick wins (easy + high impact)
        phase1 = [
            opp for opp in opportunities
            if opp.effort.value <= EffortLevel.EASY.value
            and opp.impact.value >= ImpactLevel.HIGH.value
        ]
        
        # Phase 2: Critical fixes (regardless of effort)
        phase2 = [
            opp for opp in opportunities
            if opp.impact == ImpactLevel.CRITICAL
            and opp not in phase1
        ]
        
        # Phase 3: High value optimizations
        phase3 = [
            opp for opp in opportunities
            if opp.impact.value >= ImpactLevel.HIGH.value
            and opp not in phase1
            and opp not in phase2
        ]
        
        # Phase 4: Medium priority
        phase4 = [
            opp for opp in opportunities
            if opp.impact == ImpactLevel.MEDIUM
            and opp not in phase1
            and opp not in phase2
            and opp not in phase3
        ]
        
        # Phase 5: Nice to have
        phase5 = [
            opp for opp in opportunities
            if opp not in phase1
            and opp not in phase2
            and opp not in phase3
            and opp not in phase4
        ]
        
        return {
            "Phase 1 - Quick Wins": phase1,
            "Phase 2 - Critical Fixes": phase2,
            "Phase 3 - High Value": phase3,
            "Phase 4 - Medium Priority": phase4,
            "Phase 5 - Nice to Have": phase5
        }
    
    def _calculate_priority(self, impact: ImpactLevel, effort: EffortLevel) -> float:
        """
        Calculate priority score based on impact and effort.
        
        Uses formula: Priority = Impact / Effort
        Higher score = higher priority
        
        Args:
            impact: Impact level
            effort: Effort level
            
        Returns:
            Priority score
        """
        return impact.value / effort.value
    
    def _count_by_attribute(self, attribute: str, opportunities: List[OptimizationOpportunity]) -> Dict[str, int]:
        """Count opportunities by attribute value."""
        counts = {}
        for opp in opportunities:
            value = getattr(opp, attribute)
            key = value.name if hasattr(value, 'name') else str(value)
            counts[key] = counts.get(key, 0) + 1
        return counts
    
    @staticmethod
    def create_from_analysis(
        issues: List[Any],
        bottlenecks: List[Any],
        patterns: List[Any]
    ) -> 'OptimizationRanker':
        """
        Create optimization ranker from analysis results.
        
        Args:
            issues: List of code issues
            bottlenecks: List of performance bottlenecks
            patterns: List of detected patterns
            
        Returns:
            Configured OptimizationRanker
        """
        ranker = OptimizationRanker()
        
        # Convert issues to opportunities
        severity_to_impact = {
            'critical': ImpactLevel.CRITICAL,
            'high': ImpactLevel.HIGH,
            'medium': ImpactLevel.MEDIUM,
            'low': ImpactLevel.LOW
        }
        
        for issue in issues:
            impact = severity_to_impact.get(issue.severity, ImpactLevel.LOW)
            effort = EffortLevel.EASY if impact.value <= 2 else EffortLevel.MODERATE
            
            ranker.add_opportunity(
                title=f"{issue.category}: {issue.message}",
                description=issue.message,
                category=issue.category,
                impact=impact,
                effort=effort,
                line_number=issue.line_number,
                estimated_improvement="Improves code quality",
                implementation_steps=[issue.suggestion],
                risks=[]
            )
        
        # Convert bottlenecks to opportunities
        for bottleneck in bottlenecks:
            impact = severity_to_impact.get(bottleneck.severity, ImpactLevel.LOW)
            effort = EffortLevel.MODERATE if impact.value >= 4 else EffortLevel.EASY
            
            ranker.add_opportunity(
                title=f"Performance: {bottleneck.description}",
                description=f"{bottleneck.description}\nImpact: {bottleneck.impact}",
                category="performance",
                impact=impact,
                effort=effort,
                line_number=bottleneck.line_number,
                estimated_improvement=bottleneck.estimated_improvement,
                implementation_steps=[bottleneck.optimization_suggestion],
                risks=["May require algorithm restructuring"]
            )
        
        return ranker