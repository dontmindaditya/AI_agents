"""
Syllabus Generator Agent - Creates structured syllabus from agent discussions
"""

from typing import Optional, Dict, Any
from langchain_core.language_models.base import BaseLanguageModel
from agents.base_agent import BaseAgent
from config.prompts import prompts
from models.llm_provider import create_syllabus_llm


class SyllabusGenerator(BaseAgent):
    """
    Agent responsible for synthesizing discussion into a comprehensive syllabus
    
    Takes the conversation between Agent 1 and Agent 2 and generates
    a structured, detailed syllabus for the learning topic
    """
    
    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        **kwargs
    ):
        """
        Initialize the Syllabus Generator
        
        Args:
            llm: Optional pre-configured LLM (will use syllabus-optimized if not provided)
            **kwargs: Additional configuration
        """
        # Use syllabus-optimized LLM if not provided
        llm = llm or create_syllabus_llm()
        
        super().__init__(
            name="SyllabusGenerator",
            system_prompt=prompts.SYLLABUS_GENERATION_SYSTEM,
            llm=llm,
            temperature=0.6,  # Lower temperature for more structured output
            max_tokens=3000,  # Higher token limit for comprehensive syllabus
            **kwargs
        )
        
        self.generated_syllabus: Optional[str] = None
        self.topic: Optional[str] = None
    
    def generate_from_discussion(
        self,
        topic: str,
        discussion_history: str,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Generate syllabus from discussion history
        
        Args:
            topic: The learning topic
            discussion_history: Formatted discussion between agents
            custom_prompt: Optional custom prompt template
            
        Returns:
            Generated syllabus as formatted text
        """
        self.topic = topic
        
        # Prepare the generation prompt
        if custom_prompt:
            prompt = custom_prompt.format(
                topic=topic,
                discussion_history=discussion_history
            )
        else:
            prompt = prompts.SYLLABUS_GENERATION_PROMPT.format(
                topic=topic,
                discussion_history=discussion_history
            )
        
        self.logger.info(f"Generating syllabus for: {topic}")
        self.logger.debug(f"Discussion history length: {len(discussion_history)} chars")
        
        # Generate syllabus
        try:
            syllabus = self.get_response(
                prompt,
                include_history=False,
                add_to_history=True
            )
            
            self.generated_syllabus = syllabus
            self.logger.info(f"Successfully generated syllabus ({len(syllabus)} chars)")
            
            return syllabus
            
        except Exception as e:
            self.logger.error(f"Error generating syllabus: {str(e)}")
            raise
    
    def refine_syllabus(
        self,
        feedback: str,
        current_syllabus: Optional[str] = None
    ) -> str:
        """
        Refine the syllabus based on feedback
        
        Args:
            feedback: Feedback or refinement instructions
            current_syllabus: Optional syllabus to refine (uses last generated if not provided)
            
        Returns:
            Refined syllabus
        """
        syllabus_to_refine = current_syllabus or self.generated_syllabus
        
        if not syllabus_to_refine:
            raise ValueError("No syllabus available to refine")
        
        refinement_prompt = f"""Here is the current syllabus:

{syllabus_to_refine}

Please refine this syllabus based on the following feedback:
{feedback}

Provide the complete refined syllabus:"""
        
        self.logger.info("Refining syllabus based on feedback")
        
        refined = self.get_response(
            refinement_prompt,
            include_history=False,
            add_to_history=True
        )
        
        self.generated_syllabus = refined
        return refined
    
    def extract_syllabus_structure(self) -> Dict[str, Any]:
        """
        Extract structured information from the generated syllabus
        
        Returns:
            Dictionary with syllabus components
        """
        if not self.generated_syllabus:
            raise ValueError("No syllabus has been generated yet")
        
        # Use LLM to extract structure
        extraction_prompt = f"""Analyze this syllabus and extract its structure in the following JSON format:
{{
    "title": "course title",
    "overview": "brief overview",
    "prerequisites": ["prerequisite1", "prerequisite2"],
    "modules": [
        {{
            "title": "module title",
            "duration": "estimated duration",
            "topics": ["topic1", "topic2"],
            "objectives": ["objective1", "objective2"]
        }}
    ],
    "total_duration": "estimated total duration"
}}

Syllabus:
{self.generated_syllabus}

Provide ONLY the JSON output, no additional text:"""
        
        try:
            import json
            structure_json = self.get_response(
                extraction_prompt,
                include_history=False,
                add_to_history=False
            )
            
            # Try to parse JSON
            structure = json.loads(structure_json)
            return structure
            
        except Exception as e:
            self.logger.warning(f"Could not extract structured format: {str(e)}")
            # Return basic structure
            return {
                "title": self.topic,
                "raw_syllabus": self.generated_syllabus
            }
    
    def get_syllabus_overview(self) -> str:
        """
        Get a brief overview of the syllabus
        
        Returns:
            Concise overview suitable for introduction
        """
        if not self.generated_syllabus:
            raise ValueError("No syllabus has been generated yet")
        
        overview_prompt = f"""Provide a brief 2-3 sentence overview of this syllabus that could be used to introduce it to a student:

{self.generated_syllabus}

Overview:"""
        
        overview = self.get_response(
            overview_prompt,
            include_history=False,
            add_to_history=False
        )
        
        return overview
    
    def process(
        self,
        topic: str,
        discussion_history: str,
        **kwargs
    ) -> str:
        """
        Main processing method - generates syllabus from discussion
        
        Args:
            topic: Learning topic
            discussion_history: Discussion between agents
            **kwargs: Additional parameters
            
        Returns:
            Generated syllabus
        """
        return self.generate_from_discussion(topic, discussion_history)
    
    def reset(self):
        """Reset the generator"""
        super().reset()
        self.generated_syllabus = None
        self.topic = None


class SyllabusFormatter:
    """Utility class for formatting and exporting syllabus"""
    
    @staticmethod
    def format_as_markdown(syllabus: str, title: Optional[str] = None) -> str:
        """Format syllabus as Markdown"""
        formatted = []
        
        if title:
            formatted.append(f"# {title}\n")
        
        formatted.append(syllabus)
        
        return "\n".join(formatted)
    
    @staticmethod
    def format_as_html(syllabus: str, title: Optional[str] = None) -> str:
        """Format syllabus as HTML"""
        html = ["<!DOCTYPE html>", "<html>", "<head>"]
        
        if title:
            html.append(f"<title>{title}</title>")
        
        html.extend([
            "<style>",
            "body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }",
            "h1, h2, h3 { color: #333; }",
            "pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }",
            "</style>",
            "</head>",
            "<body>"
        ])
        
        if title:
            html.append(f"<h1>{title}</h1>")
        
        # Convert markdown-style headers to HTML
        for line in syllabus.split('\n'):
            if line.startswith('# '):
                html.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                html.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                html.append(f"<h3>{line[4:]}</h3>")
            else:
                html.append(f"<p>{line}</p>")
        
        html.extend(["</body>", "</html>"])
        
        return "\n".join(html)
    
    @staticmethod
    def save_to_file(syllabus: str, filepath: str, format: str = "txt"):
        """Save syllabus to file"""
        content = syllabus
        
        if format == "md":
            content = SyllabusFormatter.format_as_markdown(syllabus)
        elif format == "html":
            content = SyllabusFormatter.format_as_html(syllabus)
        
        with open(filepath, 'w') as f:
            f.write(content)