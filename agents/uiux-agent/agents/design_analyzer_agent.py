"""
Design Analyzer Agent - Analyzes UI/UX designs from images
"""
from crewai import Agent, Task
from typing import Dict, Any, Optional
import json

from utils.llm_client import llm_client
from utils import prompts
from tools import ImageProcessor, ColorExtractor, LayoutDetector, ComponentIdentifier, MetricsCalculator
from models.schemas import DesignAnalysis, ColorPalette, LayoutMetrics, UIComponent, ComponentType


class DesignAnalyzerAgent:
    """Agent specialized in analyzing UI/UX designs"""
    
    def __init__(self):
        self.agent = Agent(
            role="UI/UX Design Analyst",
            goal="Analyze UI/UX designs and extract comprehensive design information",
            backstory=prompts.DESIGN_ANALYZER_SYSTEM_PROMPT,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_design(
        self,
        image_data: bytes,
        user_context: Optional[str] = None
    ) -> DesignAnalysis:
        """
        Analyze a design image comprehensively
        
        Args:
            image_data: Raw image bytes
            user_context: Optional user context/requirements
            
        Returns:
            DesignAnalysis object with complete analysis
        """
        # Step 1: Process image with computer vision
        cv_image, pil_image = ImageProcessor.load_image(image_data)
        
        # Step 2: Extract visual features
        dimensions = ImageProcessor.get_dimensions(cv_image)
        rectangles = ImageProcessor.detect_rectangles(cv_image, min_area=2000)
        
        # Step 3: Analyze layout
        layout_analysis = LayoutDetector.analyze_layout(cv_image)
        
        # Step 4: Extract colors
        color_palette_dict = ColorExtractor.extract_palette(pil_image)
        
        # Step 5: Identify components
        components_raw = ComponentIdentifier.identify_components(rectangles, dimensions)
        
        # Step 6: Calculate metrics
        metrics = MetricsCalculator.calculate_all_metrics(
            components_raw,
            layout_analysis,
            dimensions
        )
        
        # Step 7: Use LLM for high-level analysis
        # Convert image to base64 for LLM
        from utils.validators import ImageValidator
        image_b64 = ImageValidator.image_to_base64(image_data, "png")
        
        # Prepare analysis prompt with CV results
        cv_analysis_summary = {
            "dimensions": dimensions,
            "layout_type": layout_analysis["layout_type"],
            "components_detected": len(components_raw),
            "component_types": list(ComponentIdentifier.estimate_component_count(components_raw).keys()),
            "color_palette": color_palette_dict,
            "metrics": metrics
        }
        
        prompt = f"""Analyze this UI/UX design image.

Computer Vision Analysis:
{json.dumps(cv_analysis_summary, indent=2)}

User Context: {user_context or "No additional context"}

Provide a comprehensive design analysis including:
1. Design style (modern, minimal, material, neumorphic, etc.)
2. Overall assessment and summary
3. Key design patterns observed
4. Responsive readiness assessment

Respond in JSON format with keys: design_style, summary, responsive_ready"""
        
        llm_response = llm_client.generate_json(
            prompt=prompt,
            system_prompt=prompts.DESIGN_ANALYZER_SYSTEM_PROMPT,
            schema={
                "design_style": "string",
                "summary": "string",
                "responsive_ready": "boolean"
            }
        )
        
        # Step 8: Assemble final analysis
        color_palette = ColorPalette(
            primary=color_palette_dict.get("primary", "#000000"),
            secondary=color_palette_dict.get("secondary"),
            accent=color_palette_dict.get("accent"),
            background=color_palette_dict.get("background", "#FFFFFF"),
            text=color_palette_dict.get("text", "#000000"),
            all_colors=color_palette_dict.get("all_colors", [])
        )
        
        layout_metrics = LayoutMetrics(
            width=dimensions["width"],
            height=dimensions["height"],
            aspect_ratio=dimensions["aspect_ratio"],
            spacing_consistency=layout_analysis.get("spacing_consistency", 0.5),
            alignment_score=layout_analysis.get("alignment_score", 0.5),
            grid_detected=layout_analysis.get("grid_detected", False),
            columns=layout_analysis.get("columns"),
            rows=layout_analysis.get("rows")
        )
        
        # Convert components
        ui_components = []
        for comp in components_raw:
            ui_comp = UIComponent(
                type=ComponentType(comp["type"]) if comp["type"] in ComponentType.__members__.values() else ComponentType.CONTAINER,
                confidence=comp["confidence"],
                position=comp["position"],
                properties=comp.get("properties", {}),
                style_properties={}
            )
            ui_components.append(ui_comp)
        
        analysis = DesignAnalysis(
            color_palette=color_palette,
            layout_metrics=layout_metrics,
            components=ui_components,
            design_style=llm_response.get("design_style", "modern"),
            complexity_score=layout_analysis.get("complexity", 0.5),
            responsive_ready=llm_response.get("responsive_ready", True),
            summary=llm_response.get("summary", "Design analysis completed")
        )
        
        return analysis
    
    def create_task(self, image_data: bytes, context: Optional[str] = None) -> Task:
        """Create a CrewAI task for design analysis"""
        return Task(
            description=f"Analyze the provided UI/UX design image. Context: {context or 'None'}",
            agent=self.agent,
            expected_output="Comprehensive design analysis including colors, layout, components, and style"
        )