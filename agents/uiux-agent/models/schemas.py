"""
Data schemas and models for UI/UX Agent
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ComponentType(str, Enum):
    """UI Component types"""
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    NAVBAR = "navbar"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    MODAL = "modal"
    FORM = "form"
    TABLE = "table"
    IMAGE = "image"
    TEXT = "text"
    ICON = "icon"
    CONTAINER = "container"
    GRID = "grid"
    LIST = "list"


class ColorPalette(BaseModel):
    """Color palette extracted from design"""
    primary: str = Field(description="Primary color hex code")
    secondary: Optional[str] = Field(None, description="Secondary color hex code")
    accent: Optional[str] = Field(None, description="Accent color hex code")
    background: str = Field(description="Background color hex code")
    text: str = Field(description="Text color hex code")
    all_colors: List[str] = Field(default_factory=list, description="All extracted colors")


class LayoutMetrics(BaseModel):
    """Layout and spacing metrics"""
    width: int
    height: int
    aspect_ratio: float
    spacing_consistency: float = Field(ge=0, le=1, description="0-1 score for spacing consistency")
    alignment_score: float = Field(ge=0, le=1, description="0-1 score for alignment")
    grid_detected: bool = Field(default=False)
    columns: Optional[int] = None
    rows: Optional[int] = None


class UIComponent(BaseModel):
    """Detected UI component"""
    type: ComponentType
    confidence: float = Field(ge=0, le=1)
    position: Dict[str, int] = Field(description="x, y, width, height")
    properties: Dict[str, Any] = Field(default_factory=dict)
    text_content: Optional[str] = None
    style_properties: Dict[str, str] = Field(default_factory=dict)


class DesignAnalysis(BaseModel):
    """Complete design analysis result"""
    color_palette: ColorPalette
    layout_metrics: LayoutMetrics
    components: List[UIComponent]
    design_style: str = Field(description="modern, minimal, vintage, etc.")
    complexity_score: float = Field(ge=0, le=1)
    responsive_ready: bool
    summary: str


class UXRecommendation(BaseModel):
    """UX improvement recommendation"""
    category: str = Field(description="accessibility, usability, performance, etc.")
    severity: str = Field(description="low, medium, high, critical")
    title: str
    description: str
    suggestion: str
    impact: str = Field(description="Expected impact of implementing the suggestion")


class AccessibilityIssue(BaseModel):
    """Accessibility issue detected"""
    wcag_level: str = Field(description="A, AA, AAA")
    guideline: str = Field(description="WCAG guideline number")
    issue: str
    recommendation: str
    element: Optional[str] = None


class GeneratedCode(BaseModel):
    """Generated code output"""
    framework: str = Field(description="react, html, vue")
    component_code: str
    styles_code: str
    props_interface: Optional[str] = None
    imports: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    usage_example: str


class AgentResponse(BaseModel):
    """Final agent response"""
    success: bool
    message: str
    design_analysis: Optional[DesignAnalysis] = None
    generated_code: Optional[GeneratedCode] = None
    ux_recommendations: List[UXRecommendation] = Field(default_factory=list)
    accessibility_issues: List[AccessibilityIssue] = Field(default_factory=list)
    execution_time: float
    agent_thoughts: List[str] = Field(default_factory=list, description="Agent reasoning process")