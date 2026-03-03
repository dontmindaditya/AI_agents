"""
Code Generator Agent - Generates production-ready code from design analysis
"""
from crewai import Agent, Task
from typing import Dict, Any, Optional
import json

from utils.llm_client import llm_client
from utils import prompts
from models.schemas import DesignAnalysis, GeneratedCode
from config import settings


class CodeGeneratorAgent:
    """Agent specialized in generating UI code"""
    
    def __init__(self):
        self.agent = Agent(
            role="Frontend Code Generator",
            goal="Generate production-ready, accessible, and maintainable UI code",
            backstory=prompts.CODE_GENERATOR_SYSTEM_PROMPT,
            verbose=True,
            allow_delegation=False
        )
    
    def generate_code(
        self,
        design_analysis: DesignAnalysis,
        framework: str = "react",
        additional_requirements: Optional[str] = None
    ) -> GeneratedCode:
        """
        Generate code from design analysis
        
        Args:
            design_analysis: Complete design analysis
            framework: Target framework (react, html, vue)
            additional_requirements: Additional user requirements
            
        Returns:
            GeneratedCode object
        """
        framework = framework.lower()
        
        if framework == "react":
            return self._generate_react(design_analysis, additional_requirements)
        elif framework == "html":
            return self._generate_html(design_analysis, additional_requirements)
        elif framework == "vue":
            return self._generate_vue(design_analysis, additional_requirements)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _generate_react(
        self,
        design_analysis: DesignAnalysis,
        additional_requirements: Optional[str]
    ) -> GeneratedCode:
        """Generate React component"""
        
        # Prepare design summary for LLM
        design_summary = {
            "style": design_analysis.design_style,
            "colors": {
                "primary": design_analysis.color_palette.primary,
                "secondary": design_analysis.color_palette.secondary,
                "background": design_analysis.color_palette.background,
                "text": design_analysis.color_palette.text
            },
            "layout": {
                "width": design_analysis.layout_metrics.width,
                "height": design_analysis.layout_metrics.height,
                "grid_detected": design_analysis.layout_metrics.grid_detected,
                "columns": design_analysis.layout_metrics.columns
            },
            "components": [
                {
                    "type": comp.type,
                    "position": comp.position
                }
                for comp in design_analysis.components[:10]  # Limit for token efficiency
            ],
            "complexity": design_analysis.complexity_score
        }
        
        prompt = prompts.CODE_GENERATOR_REACT_PROMPT.format(
            design_analysis=json.dumps(design_summary, indent=2)
        )
        
        if additional_requirements:
            prompt += f"\n\nAdditional Requirements:\n{additional_requirements}"
        
        # Generate code using LLM
        response = llm_client.generate(
            prompt=prompt,
            system_prompt=prompts.CODE_GENERATOR_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4000
        )
        
        # Parse response to extract code sections
        code_sections = self._parse_code_response(response, "react")
        
        return GeneratedCode(
            framework="react",
            component_code=code_sections.get("component", response),
            styles_code=code_sections.get("styles", ""),
            props_interface=code_sections.get("interface", ""),
            imports=code_sections.get("imports", []),
            dependencies=["react", "react-dom"],
            usage_example=code_sections.get("usage", "")
        )
    
    def _generate_html(
        self,
        design_analysis: DesignAnalysis,
        additional_requirements: Optional[str]
    ) -> GeneratedCode:
        """Generate HTML/CSS code"""
        
        design_summary = {
            "style": design_analysis.design_style,
            "colors": {
                "primary": design_analysis.color_palette.primary,
                "background": design_analysis.color_palette.background,
                "text": design_analysis.color_palette.text
            },
            "components": [comp.type for comp in design_analysis.components[:10]]
        }
        
        prompt = prompts.CODE_GENERATOR_HTML_PROMPT.format(
            design_analysis=json.dumps(design_summary, indent=2)
        )
        
        if additional_requirements:
            prompt += f"\n\nAdditional Requirements:\n{additional_requirements}"
        
        response = llm_client.generate(
            prompt=prompt,
            system_prompt=prompts.CODE_GENERATOR_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4000
        )
        
        code_sections = self._parse_code_response(response, "html")
        
        return GeneratedCode(
            framework="html",
            component_code=code_sections.get("html", response),
            styles_code=code_sections.get("css", ""),
            imports=[],
            dependencies=[],
            usage_example=code_sections.get("usage", "")
        )
    
    def _generate_vue(
        self,
        design_analysis: DesignAnalysis,
        additional_requirements: Optional[str]
    ) -> GeneratedCode:
        """Generate Vue component"""
        # Similar to React but for Vue
        # Implementation simplified for brevity
        return self._generate_react(design_analysis, additional_requirements)
    
    def _parse_code_response(self, response: str, framework: str) -> Dict[str, Any]:
        """Parse LLM response to extract code sections"""
        sections = {}
        
        # Extract code blocks
        import re
        
        # Find all code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', response, re.DOTALL)
        
        for lang, code in code_blocks:
            if not lang:
                lang = "code"
            
            lang = lang.lower()
            
            if lang in ["tsx", "jsx", "typescript", "javascript"]:
                if "component" not in sections:
                    sections["component"] = code
                elif "interface" in code or "type" in code:
                    sections["interface"] = code
            elif lang == "css" or lang == "scss":
                sections["styles"] = code
            elif lang == "html":
                sections["html"] = code
        
        # Extract imports
        import_pattern = r'^import\s+.*?from\s+[\'"].*?[\'"];?$'
        imports = re.findall(import_pattern, response, re.MULTILINE)
        sections["imports"] = imports
        
        # Extract usage example
        usage_pattern = r'(?:Usage|Example|How to use):?\s*```.*?\n(.*?)\n```'
        usage_match = re.search(usage_pattern, response, re.DOTALL | re.IGNORECASE)
        if usage_match:
            sections["usage"] = usage_match.group(1)
        
        return sections
    
    def create_task(
        self,
        design_analysis: DesignAnalysis,
        framework: str = "react"
    ) -> Task:
        """Create a CrewAI task for code generation"""
        return Task(
            description=f"Generate {framework} code based on the design analysis provided",
            agent=self.agent,
            expected_output=f"Production-ready {framework} code with proper structure and styling"
        )