"""
Orchestrator Agent - Coordinates all specialized agents
"""
from crewai import Crew
from typing import Optional, Dict, Any
import time

from agents.design_analyzer_agent import DesignAnalyzerAgent
from agents.code_generator_agent import CodeGeneratorAgent
from agents.ux_advisor_agent import UXAdvisorAgent
from agents.accessibility_agent import AccessibilityAgent
from agents.layout_optimizer_agent import LayoutOptimizerAgent

from models.schemas import AgentResponse
from models.agent_state import AgentState
from utils.validators import ImageValidator, TaskValidator
from config import settings


class OrchestratorAgent:
    """
    Main orchestrator that coordinates all specialized agents
    """
    
    def __init__(self):
        # Initialize all specialized agents
        self.design_analyzer = DesignAnalyzerAgent()
        self.code_generator = CodeGeneratorAgent()
        self.ux_advisor = UXAdvisorAgent()
        self.accessibility_agent = AccessibilityAgent()
        self.layout_optimizer = LayoutOptimizerAgent()
    
    def execute(
        self,
        task: str,
        image_path: Optional[str] = None,
        image_data: Optional[bytes] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute the complete UI/UX agent workflow
        
        Args:
            task: User's task description
            image_path: Path to design image (optional)
            image_data: Raw image bytes (optional)
            user_preferences: User preferences (framework, style, etc.)
            
        Returns:
            Complete agent response with all analysis and generated outputs
        """
        start_time = time.time()
        
        # Initialize state
        state = AgentState(
            task=task,
            image_path=image_path,
            image_data=image_data,
            user_preferences=user_preferences or {}
        )
        
        try:
            # Validate task
            task = TaskValidator.validate_task(task)
            state.add_thought("Task validated successfully")
            
            # Load image if provided
            if image_path:
                state.add_thought(f"Loading image from path: {image_path}")
                image_data, _ = ImageValidator.load_image(image_path)
                state.image_data = image_data
            elif image_data:
                state.add_thought("Using provided image data")
                ImageValidator.validate_image_data(image_data)
            else:
                # No image provided - text-only mode
                state.add_thought("No image provided - operating in text mode")
            
            # Step 1: Design Analysis (if image provided)
            if state.image_data:
                state.update_step("design_analysis")
                state.add_thought("Starting design analysis...")
                
                design_analysis = self.design_analyzer.analyze_design(
                    image_data=state.image_data,
                    user_context=task
                )
                
                state.design_analysis = design_analysis
                state.add_thought(f"Design analysis complete. Style: {design_analysis.design_style}")
            
            # Step 2: Code Generation (if requested and design analyzed)
            if state.design_analysis and self._should_generate_code(task, user_preferences):
                state.update_step("code_generation")
                framework = user_preferences.get("framework", settings.output_code_format)
                state.add_thought(f"Generating {framework} code...")
                
                generated_code = self.code_generator.generate_code(
                    design_analysis=state.design_analysis,
                    framework=framework,
                    additional_requirements=task
                )
                
                state.generated_code = generated_code
                state.add_thought("Code generation complete")
            
            # Step 3: UX Analysis
            if state.design_analysis:
                state.update_step("ux_analysis")
                state.add_thought("Analyzing UX...")
                
                ux_recommendations = self.ux_advisor.analyze_ux(
                    design_analysis=state.design_analysis,
                    generated_code=state.generated_code
                )
                
                state.ux_recommendations = ux_recommendations
                state.add_thought(f"Found {len(ux_recommendations)} UX recommendations")
            
            # Step 4: Accessibility Audit
            if state.design_analysis:
                state.update_step("accessibility_audit")
                state.add_thought("Performing accessibility audit...")
                
                accessibility_issues = self.accessibility_agent.audit_accessibility(
                    design_analysis=state.design_analysis,
                    generated_code=state.generated_code
                )
                
                state.accessibility_issues = accessibility_issues
                state.add_thought(f"Found {len(accessibility_issues)} accessibility issues")
            
            # Complete execution
            state.mark_complete()
            execution_time = time.time() - start_time
            
            # Build response
            response = AgentResponse(
                success=True,
                message=self._generate_success_message(state),
                design_analysis=state.design_analysis,
                generated_code=state.generated_code,
                ux_recommendations=state.ux_recommendations,
                accessibility_issues=state.accessibility_issues,
                execution_time=execution_time,
                agent_thoughts=state.agent_thoughts
            )
            
            return response
            
        except Exception as e:
            state.mark_error(str(e))
            execution_time = time.time() - start_time
            
            return AgentResponse(
                success=False,
                message=f"Error during execution: {str(e)}",
                execution_time=execution_time,
                agent_thoughts=state.agent_thoughts
            )
    
    def _should_generate_code(
        self,
        task: str,
        user_preferences: Optional[Dict[str, Any]]
    ) -> bool:
        """Determine if code generation is needed"""
        if user_preferences and user_preferences.get("generate_code") is False:
            return False
        
        # Check if task mentions code generation
        code_keywords = ["generate", "create", "build", "code", "component", "implement"]
        task_lower = task.lower()
        
        return any(keyword in task_lower for keyword in code_keywords)
    
    def _generate_success_message(self, state: AgentState) -> str:
        """Generate a success message based on what was accomplished"""
        parts = []
        
        if state.design_analysis:
            parts.append("✓ Design analysis completed")
        
        if state.generated_code:
            parts.append(f"✓ {state.generated_code.framework.upper()} code generated")
        
        if state.ux_recommendations:
            parts.append(f"✓ {len(state.ux_recommendations)} UX recommendations")
        
        if state.accessibility_issues:
            critical = len([i for i in state.accessibility_issues if "AA" in i.wcag_level])
            parts.append(f"✓ {len(state.accessibility_issues)} accessibility issues found ({critical} critical)")
        
        return " | ".join(parts) if parts else "Task completed successfully"
    
    def execute_with_crew(
        self,
        task: str,
        image_data: Optional[bytes] = None
    ) -> AgentResponse:
        """
        Alternative execution using CrewAI's Crew for full agent collaboration
        
        Args:
            task: User task
            image_data: Optional image data
            
        Returns:
            Agent response
        """
        # This is an alternative approach using CrewAI's crew system
        # Not fully implemented here but shows the pattern
        
        if not image_data:
            raise ValueError("Image data required for crew execution")
        
        # Analyze design first
        design_analysis = self.design_analyzer.analyze_design(image_data, task)
        
        # Create tasks for each agent
        tasks = [
            self.code_generator.create_task(design_analysis, "react"),
            self.ux_advisor.create_task(design_analysis),
            self.accessibility_agent.create_task(design_analysis)
        ]
        
        # Create crew
        crew = Crew(
            agents=[
                self.code_generator.agent,
                self.ux_advisor.agent,
                self.accessibility_agent.agent
            ],
            tasks=tasks,
            verbose=True
        )
        
        # Execute crew
        result = crew.kickoff()
        
        # Build response (simplified)
        return AgentResponse(
            success=True,
            message="Crew execution completed",
            design_analysis=design_analysis,
            execution_time=0.0
        )