"""
Accessibility Agent - Checks WCAG compliance and accessibility issues
"""
from crewai import Agent, Task
from typing import List, Optional
import json

from utils.llm_client import llm_client
from utils import prompts
from models.schemas import DesignAnalysis, GeneratedCode, AccessibilityIssue
from tools.color_extractor import ColorExtractor


class AccessibilityAgent:
    """Agent specialized in accessibility compliance (WCAG 2.1)"""
    
    def __init__(self):
        self.agent = Agent(
            role="Accessibility Specialist (WCAG Expert)",
            goal="Identify accessibility issues and ensure WCAG 2.1 compliance",
            backstory=prompts.ACCESSIBILITY_SYSTEM_PROMPT,
            verbose=True,
            allow_delegation=False
        )
    
    def audit_accessibility(
        self,
        design_analysis: DesignAnalysis,
        generated_code: Optional[GeneratedCode] = None
    ) -> List[AccessibilityIssue]:
        """
        Perform accessibility audit
        
        Args:
            design_analysis: Design analysis results
            generated_code: Optional generated code
            
        Returns:
            List of accessibility issues
        """
        issues = []
        
        # 1. Check color contrast
        issues.extend(self._check_color_contrast(design_analysis))
        
        # 2. Use LLM for comprehensive audit
        design_context = {
            "colors": {
                "primary": design_analysis.color_palette.primary,
                "background": design_analysis.color_palette.background,
                "text": design_analysis.color_palette.text
            },
            "components": [comp.type for comp in design_analysis.components[:20]]
        }
        
        code_summary = "No code provided"
        if generated_code:
            code_summary = f"Framework: {generated_code.framework}\n{generated_code.component_code[:500]}..."
        
        prompt = prompts.ACCESSIBILITY_PROMPT.format(
            design_analysis=json.dumps(design_context, indent=2),
            code_summary=code_summary
        )
        
        response = llm_client.generate_json(
            prompt=prompt,
            system_prompt=prompts.ACCESSIBILITY_SYSTEM_PROMPT,
            schema={
                "issues": [
                    {
                        "wcag_level": "string",
                        "guideline": "string",
                        "issue": "string",
                        "recommendation": "string",
                        "element": "string"
                    }
                ]
            }
        )
        
        # Parse LLM issues
        for issue_data in response.get("issues", []):
            try:
                issue = AccessibilityIssue(
                    wcag_level=issue_data.get("wcag_level", "AA"),
                    guideline=issue_data.get("guideline", ""),
                    issue=issue_data.get("issue", ""),
                    recommendation=issue_data.get("recommendation", ""),
                    element=issue_data.get("element")
                )
                issues.append(issue)
            except Exception as e:
                print(f"Error parsing accessibility issue: {e}")
                continue
        
        return issues
    
    def _check_color_contrast(
        self,
        design_analysis: DesignAnalysis
    ) -> List[AccessibilityIssue]:
        """Check color contrast ratios for WCAG compliance"""
        issues = []
        
        primary = design_analysis.color_palette.primary
        background = design_analysis.color_palette.background
        text = design_analysis.color_palette.text
        
        # Check text on background
        text_bg_ratio = ColorExtractor.calculate_contrast_ratio(text, background)
        
        if text_bg_ratio < 4.5:
            issues.append(AccessibilityIssue(
                wcag_level="AA",
                guideline="1.4.3",
                issue=f"Text color contrast ratio is {text_bg_ratio:.2f}:1, which is below the WCAG AA minimum of 4.5:1",
                recommendation=f"Increase contrast between text ({text}) and background ({background}). Consider darkening text or lightening background.",
                element="text"
            ))
        elif text_bg_ratio < 7.0:
            # Meets AA but not AAA
            issues.append(AccessibilityIssue(
                wcag_level="AAA",
                guideline="1.4.6",
                issue=f"Text color contrast ratio is {text_bg_ratio:.2f}:1, which meets AA but not AAA (7:1)",
                recommendation=f"For AAA compliance, increase contrast to at least 7:1",
                element="text"
            ))
        
        # Check primary color on background (for buttons, links, etc.)
        primary_bg_ratio = ColorExtractor.calculate_contrast_ratio(primary, background)
        
        if primary_bg_ratio < 3.0:
            issues.append(AccessibilityIssue(
                wcag_level="AA",
                guideline="1.4.11",
                issue=f"Primary color contrast with background is {primary_bg_ratio:.2f}:1, below minimum 3:1 for UI components",
                recommendation=f"Increase contrast between primary color ({primary}) and background ({background})",
                element="primary-elements"
            ))
        
        return issues
    
    def _check_semantic_html(self, code: str) -> List[AccessibilityIssue]:
        """Check for semantic HTML usage"""
        issues = []
        
        # Check for semantic elements
        required_elements = {
            "nav": "navigation",
            "main": "main content",
            "header": "page header",
            "footer": "page footer",
            "button": "interactive buttons"
        }
        
        for element, purpose in required_elements.items():
            if f"<{element}" not in code.lower() and element != "button":
                issues.append(AccessibilityIssue(
                    wcag_level="A",
                    guideline="4.1.2",
                    issue=f"Missing semantic <{element}> element for {purpose}",
                    recommendation=f"Use <{element}> instead of generic <div> for {purpose}",
                    element=element
                ))
        
        # Check for div buttons (should use <button>)
        if "onclick" in code.lower() and "<button" not in code.lower():
            issues.append(AccessibilityIssue(
                wcag_level="A",
                guideline="4.1.2",
                issue="Interactive elements using div with onClick instead of proper button elements",
                recommendation="Use <button> elements for interactive actions instead of divs with onClick",
                element="button"
            ))
        
        return issues
    
    def create_task(
        self,
        design_analysis: DesignAnalysis,
        generated_code: Optional[GeneratedCode] = None
    ) -> Task:
        """Create a CrewAI task for accessibility audit"""
        return Task(
            description="Perform comprehensive WCAG 2.1 accessibility audit and identify issues",
            agent=self.agent,
            expected_output="List of accessibility issues with WCAG guidelines and recommendations"
        )