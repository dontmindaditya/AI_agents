"""
UX Advisor Agent - Provides UX recommendations and best practices
"""
from crewai import Agent, Task
from typing import List, Optional
import json

from utils.llm_client import llm_client
from utils import prompts
from models.schemas import DesignAnalysis, GeneratedCode, UXRecommendation


class UXAdvisorAgent:
    """Agent specialized in UX best practices and recommendations"""
    
    def __init__(self):
        self.agent = Agent(
            role="Senior UX Consultant",
            goal="Provide actionable UX recommendations to improve user experience",
            backstory=prompts.UX_ADVISOR_SYSTEM_PROMPT,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_ux(
        self,
        design_analysis: DesignAnalysis,
        generated_code: Optional[GeneratedCode] = None
    ) -> List[UXRecommendation]:
        """
        Analyze design and code for UX improvements
        
        Args:
            design_analysis: Design analysis results
            generated_code: Optional generated code
            
        Returns:
            List of UX recommendations
        """
        # Prepare context for LLM
        design_context = {
            "style": design_analysis.design_style,
            "complexity": design_analysis.complexity_score,
            "responsive": design_analysis.responsive_ready,
            "components": [
                {"type": comp.type, "count": 1}
                for comp in design_analysis.components[:15]
            ],
            "layout_metrics": {
                "spacing_consistency": design_analysis.layout_metrics.spacing_consistency,
                "alignment_score": design_analysis.layout_metrics.alignment_score,
                "grid_detected": design_analysis.layout_metrics.grid_detected
            }
        }
        
        code_summary = "No code available"
        if generated_code:
            code_summary = f"Framework: {generated_code.framework}, Components generated"
        
        prompt = prompts.UX_ADVISOR_PROMPT.format(
            design_analysis=json.dumps(design_context, indent=2),
            code_summary=code_summary
        )
        
        response = llm_client.generate_json(
            prompt=prompt,
            system_prompt=prompts.UX_ADVISOR_SYSTEM_PROMPT,
            schema={
                "recommendations": [
                    {
                        "category": "string",
                        "severity": "string",
                        "title": "string",
                        "description": "string",
                        "suggestion": "string",
                        "impact": "string"
                    }
                ]
            }
        )
        
        # Parse recommendations
        recommendations = []
        for rec_data in response.get("recommendations", []):
            try:
                rec = UXRecommendation(
                    category=rec_data.get("category", "usability"),
                    severity=rec_data.get("severity", "medium"),
                    title=rec_data.get("title", "UX Improvement"),
                    description=rec_data.get("description", ""),
                    suggestion=rec_data.get("suggestion", ""),
                    impact=rec_data.get("impact", "")
                )
                recommendations.append(rec)
            except Exception as e:
                print(f"Error parsing recommendation: {e}")
                continue
        
        # Add heuristic-based recommendations
        recommendations.extend(self._get_heuristic_recommendations(design_analysis))
        
        return recommendations
    
    def _get_heuristic_recommendations(
        self,
        design_analysis: DesignAnalysis
    ) -> List[UXRecommendation]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        # Check spacing consistency
        if design_analysis.layout_metrics.spacing_consistency < 0.6:
            recommendations.append(UXRecommendation(
                category="visual_design",
                severity="medium",
                title="Inconsistent Spacing",
                description="The spacing between elements varies significantly throughout the design.",
                suggestion="Establish a consistent spacing system (e.g., 4px, 8px, 16px, 24px, 32px) and apply it uniformly across all components.",
                impact="Improved visual rhythm and professional appearance"
            ))
        
        # Check alignment
        if design_analysis.layout_metrics.alignment_score < 0.6:
            recommendations.append(UXRecommendation(
                category="visual_design",
                severity="medium",
                title="Poor Element Alignment",
                description="Elements are not well-aligned, creating a disorganized appearance.",
                suggestion="Use a grid system and ensure all elements align to grid lines. Check left, right, top, and bottom edges.",
                impact="Cleaner, more professional look and easier to scan"
            ))
        
        # Check complexity
        if design_analysis.complexity_score > 0.7:
            recommendations.append(UXRecommendation(
                category="usability",
                severity="high",
                title="High Design Complexity",
                description="The design contains many elements and may overwhelm users.",
                suggestion="Simplify by removing unnecessary elements, grouping related items, and using progressive disclosure for advanced features.",
                impact="Reduced cognitive load and improved task completion rates"
            ))
        
        # Check responsive readiness
        if not design_analysis.responsive_ready:
            recommendations.append(UXRecommendation(
                category="accessibility",
                severity="high",
                title="Not Responsive-Ready",
                description="The design may not adapt well to different screen sizes.",
                suggestion="Implement a mobile-first approach with flexible grids, breakpoints at 640px, 768px, 1024px, and 1280px.",
                impact="Better experience across all devices, reaching more users"
            ))
        
        # Check for grid usage
        if not design_analysis.layout_metrics.grid_detected:
            recommendations.append(UXRecommendation(
                category="visual_design",
                severity="low",
                title="No Clear Grid System",
                description="Elements don't follow an obvious grid structure.",
                suggestion="Implement a 12-column grid system for better organization and consistency.",
                impact="More structured layout that's easier to maintain and extend"
            ))
        
        return recommendations
    
    def create_task(self, design_analysis: DesignAnalysis) -> Task:
        """Create a CrewAI task for UX analysis"""
        return Task(
            description="Analyze the design and code for UX improvements and provide actionable recommendations",
            agent=self.agent,
            expected_output="List of prioritized UX recommendations with clear suggestions"
        )