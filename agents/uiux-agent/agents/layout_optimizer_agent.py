"""
Layout Optimizer Agent - Optimizes layout structure and spacing
"""
from crewai import Agent, Task
from typing import Dict, Any, List
import json

from utils.llm_client import llm_client
from utils import prompts
from models.schemas import DesignAnalysis


class LayoutOptimizerAgent:
    """Agent specialized in layout optimization"""
    
    def __init__(self):
        self.agent = Agent(
            role="Layout Optimization Expert",
            goal="Optimize layout structure for better visual hierarchy and performance",
            backstory=prompts.LAYOUT_OPTIMIZER_SYSTEM_PROMPT,
            verbose=True,
            allow_delegation=False
        )
    
    def optimize_layout(
        self,
        design_analysis: DesignAnalysis
    ) -> Dict[str, Any]:
        """
        Provide layout optimization recommendations
        
        Args:
            design_analysis: Design analysis results
            
        Returns:
            Dictionary with optimization recommendations
        """
        layout_context = {
            "dimensions": {
                "width": design_analysis.layout_metrics.width,
                "height": design_analysis.layout_metrics.height,
                "aspect_ratio": design_analysis.layout_metrics.aspect_ratio
            },
            "grid_detected": design_analysis.layout_metrics.grid_detected,
            "columns": design_analysis.layout_metrics.columns,
            "spacing_consistency": design_analysis.layout_metrics.spacing_consistency,
            "alignment_score": design_analysis.layout_metrics.alignment_score,
            "complexity": design_analysis.complexity_score
        }
        
        prompt = prompts.LAYOUT_OPTIMIZER_PROMPT.format(
            design_analysis=json.dumps(layout_context, indent=2)
        )
        
        response = llm_client.generate_json(
            prompt=prompt,
            system_prompt=prompts.LAYOUT_OPTIMIZER_SYSTEM_PROMPT,
            schema={
                "grid_recommendation": {
                    "type": "string",
                    "columns": "number",
                    "gutters": "string",
                    "margins": "string"
                },
                "spacing_system": ["string"],
                "breakpoints": [{"size": "string", "width": "number"}],
                "optimizations": [
                    {
                        "area": "string",
                        "suggestion": "string",
                        "css_example": "string"
                    }
                ]
            }
        )
        
        return {
            "grid_recommendation": response.get("grid_recommendation", {}),
            "spacing_system": response.get("spacing_system", []),
            "breakpoints": response.get("breakpoints", []),
            "optimizations": response.get("optimizations", []),
            "summary": self._generate_summary(response)
        }
    
    def _generate_summary(self, optimization_data: Dict[str, Any]) -> str:
        """Generate a summary of optimizations"""
        parts = []
        
        if optimization_data.get("grid_recommendation"):
            grid = optimization_data["grid_recommendation"]
            parts.append(f"Recommended grid: {grid.get('columns', 12)}-column system")
        
        if optimization_data.get("spacing_system"):
            parts.append(f"Spacing scale: {', '.join(optimization_data['spacing_system'][:5])}")
        
        if optimization_data.get("optimizations"):
            parts.append(f"{len(optimization_data['optimizations'])} layout optimizations suggested")
        
        return ". ".join(parts) if parts else "Layout analysis complete"
    
    def create_task(self, design_analysis: DesignAnalysis) -> Task:
        """Create a CrewAI task for layout optimization"""
        return Task(
            description="Analyze layout structure and provide optimization recommendations",
            agent=self.agent,
            expected_output="Comprehensive layout optimization recommendations with grid system and spacing"
        )