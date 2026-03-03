"""
Teaching Orchestrator - Coordinates the complete teaching workflow
Implements the 3-step process from the architecture
"""

from typing import Optional, Dict, Any, Callable
from agents import Agent1, Agent2, SyllabusGenerator, InstructorAgent
from agents.discussion_agents import DiscussionFacilitator
from utils.logger import create_orchestrator_logger, AgentLogger
from utils.conversation_manager import DiscussionManager
from config.settings import settings
import json
from pathlib import Path


class TeachingOrchestrator:
    """
    Main orchestrator that coordinates the complete EduGPT teaching workflow
    
    Three-step process:
    1. Initialize agents and set learning topic
    2. Facilitate discussion between agents to generate syllabus
    3. Teach the student using the generated syllabus
    """
    
    def __init__(
        self,
        topic: str,
        max_discussion_rounds: Optional[int] = None,
        save_artifacts: bool = True,
        output_dir: str = "./outputs"
    ):
        """
        Initialize the Teaching Orchestrator
        
        Args:
            topic: Learning topic to teach
            max_discussion_rounds: Maximum discussion rounds (uses config default if not provided)
            save_artifacts: Whether to save discussion and syllabus to files
            output_dir: Directory to save artifacts
        """
        self.topic = topic
        self.max_discussion_rounds = max_discussion_rounds or settings.max_discussion_rounds
        self.save_artifacts = save_artifacts
        self.output_dir = Path(output_dir)
        
        if save_artifacts:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = create_orchestrator_logger()
        self.agent_logger = AgentLogger()
        
        # Initialize components
        self.agent1: Optional[Agent1] = None
        self.agent2: Optional[Agent2] = None
        self.facilitator: Optional[DiscussionFacilitator] = None
        self.syllabus_generator: Optional[SyllabusGenerator] = None
        self.instructor: Optional[InstructorAgent] = None
        
        # State
        self.discussion_complete = False
        self.syllabus_generated = False
        self.teaching_active = False
        
        self.discussion_history: Optional[str] = None
        self.syllabus: Optional[str] = None
        
        self.logger.info(f"Initialized TeachingOrchestrator for topic: {topic}")
    
    # ========================================================================
    # STEP 1: SETUP AND INITIALIZATION
    # ========================================================================
    
    def setup(self):
        """
        Step 1: Set up agents and prepare for discussion
        
        This initializes:
        - Agent 1 (ML Instructor)
        - Agent 2 (Beginner Assistant)
        - Discussion Facilitator
        - Syllabus Generator
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 1: AGENT INITIALIZATION")
        self.logger.info("=" * 60)
        
        # Initialize discussion agents
        self.logger.info("Initializing Agent 1 (ML Instructor)...")
        self.agent1 = Agent1(topic=self.topic)
        
        self.logger.info("Initializing Agent 2 (Beginner Assistant)...")
        self.agent2 = Agent2(topic=self.topic)
        
        # Initialize facilitator
        self.logger.info("Initializing Discussion Facilitator...")
        self.facilitator = DiscussionFacilitator(
            agent1=self.agent1,
            agent2=self.agent2,
            max_rounds=self.max_discussion_rounds
        )
        
        # Initialize syllabus generator
        self.logger.info("Initializing Syllabus Generator...")
        self.syllabus_generator = SyllabusGenerator()
        
        self.logger.info("Setup complete! All agents initialized.")
        return self
    
    # ========================================================================
    # STEP 2: DISCUSSION AND SYLLABUS GENERATION
    # ========================================================================
    
    def generate_syllabus(
        self,
        discussion_callback: Optional[Callable[[int, str, str], None]] = None
    ) -> str:
        """
        Step 2: Generate syllabus through agent discussion
        
        This process:
        1. Facilitates discussion between Agent 1 and Agent 2
        2. Records the complete discussion
        3. Generates comprehensive syllabus from discussion
        
        Args:
            discussion_callback: Optional callback function called after each discussion turn
                                Signature: callback(round: int, agent: str, message: str)
        
        Returns:
            Generated syllabus
        """
        if not self.facilitator:
            raise ValueError("Orchestrator not set up. Call setup() first.")
        
        self.logger.info("=" * 60)
        self.logger.info("STEP 2: DISCUSSION AND SYLLABUS GENERATION")
        self.logger.info("=" * 60)
        
        # Phase 2A: Agent Discussion
        self.logger.info("\n>>> Phase 2A: Agent Discussion")
        self.agent_logger.log_phase_transition("Agent Discussion", self.logger)
        
        # Start discussion
        opening = self.facilitator.start_discussion()
        self.agent_logger.log_agent_message("Agent 1 (Opening)", opening, self.logger)
        
        if discussion_callback:
            discussion_callback(1, "agent1", opening)
        
        # Continue discussion
        round_num = 1
        while round_num < self.max_discussion_rounds:
            self.agent_logger.log_discussion_round(round_num + 1, self.logger)
            
            response = self.facilitator.continue_discussion()
            if response is None:
                break
            
            # Determine which agent responded
            last_entry = self.facilitator.discussion_history[-1]
            agent_name = "Agent 1" if last_entry["agent"] == "agent1" else "Agent 2"
            
            self.agent_logger.log_agent_message(agent_name, response, self.logger)
            
            if discussion_callback:
                discussion_callback(
                    last_entry["round"],
                    last_entry["agent"],
                    response
                )
            
            if last_entry["agent"] == "agent1":
                round_num += 1
        
        # Get formatted discussion
        self.discussion_history = self.facilitator.get_discussion_for_syllabus()
        self.discussion_complete = True
        
        self.logger.info(f"\nDiscussion complete! {len(self.facilitator.discussion_history)} exchanges.")
        
        # Save discussion if requested
        if self.save_artifacts:
            discussion_file = self.output_dir / f"{self._sanitize_filename(self.topic)}_discussion.txt"
            with open(discussion_file, 'w') as f:
                f.write(self.discussion_history)
            self.logger.info(f"Saved discussion to: {discussion_file}")
        
        # Phase 2B: Syllabus Generation
        self.logger.info("\n>>> Phase 2B: Syllabus Generation")
        self.agent_logger.log_phase_transition("Syllabus Generation", self.logger)
        
        self.syllabus = self.syllabus_generator.generate_from_discussion(
            topic=self.topic,
            discussion_history=self.discussion_history
        )
        
        self.syllabus_generated = True
        
        self.agent_logger.log_syllabus(self.syllabus, self.logger)
        
        # Save syllabus if requested
        if self.save_artifacts:
            syllabus_file = self.output_dir / f"{self._sanitize_filename(self.topic)}_syllabus.txt"
            with open(syllabus_file, 'w') as f:
                f.write(self.syllabus)
            self.logger.info(f"Saved syllabus to: {syllabus_file}")
            
            # Also save as markdown
            md_file = self.output_dir / f"{self._sanitize_filename(self.topic)}_syllabus.md"
            with open(md_file, 'w') as f:
                f.write(f"# {self.topic}\n\n{self.syllabus}")
            self.logger.info(f"Saved syllabus (markdown) to: {md_file}")
        
        return self.syllabus
    
    # ========================================================================
    # STEP 3: TEACHING
    # ========================================================================
    
    def start_teaching(self) -> str:
        """
        Step 3: Start teaching session with the generated syllabus
        
        Returns:
            Instructor's opening message
        """
        if not self.syllabus_generated:
            raise ValueError("Syllabus not generated. Call generate_syllabus() first.")
        
        self.logger.info("=" * 60)
        self.logger.info("STEP 3: TEACHING")
        self.logger.info("=" * 60)
        
        # Initialize instructor
        self.logger.info("Initializing Instructor Agent...")
        self.instructor = InstructorAgent(
            topic=self.topic,
            syllabus=self.syllabus
        )
        
        # Start teaching session
        self.logger.info("Starting teaching session...")
        opening_message = self.instructor.start_teaching_session()
        
        self.teaching_active = True
        
        self.agent_logger.log_agent_message("Instructor (Opening)", opening_message, self.logger)
        
        return opening_message
    
    def teach_interaction(self, student_message: str) -> str:
        """
        Handle a single teaching interaction
        
        Args:
            student_message: Message from the student
            
        Returns:
            Instructor's response
        """
        if not self.teaching_active:
            raise ValueError("Teaching not started. Call start_teaching() first.")
        
        self.logger.info(f"\nStudent: {student_message[:100]}...")
        
        response = self.instructor.teach(student_message)
        
        self.logger.info(f"Instructor: {response[:100]}...")
        
        return response
    
    def assess_student(self) -> Dict[str, Any]:
        """
        Assess student's understanding
        
        Returns:
            Assessment results
        """
        if not self.teaching_active:
            raise ValueError("Teaching not started. Call start_teaching() first.")
        
        assessment = self.instructor.assess_understanding()
        
        self.logger.info("Generated student assessment")
        
        return assessment
    
    def end_teaching(self) -> Dict[str, Any]:
        """
        End the teaching session
        
        Returns:
            Session summary
        """
        if not self.teaching_active:
            raise ValueError("Teaching not active.")
        
        summary = self.instructor.end_teaching_session()
        self.teaching_active = False
        
        self.logger.info("Teaching session ended")
        self.logger.info(f"Summary: {json.dumps(summary, indent=2)}")
        
        # Save session summary if requested
        if self.save_artifacts:
            summary_file = self.output_dir / f"{self._sanitize_filename(self.topic)}_session_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            self.logger.info(f"Saved session summary to: {summary_file}")
        
        return summary
    
    # ========================================================================
    # COMPLETE WORKFLOW
    # ========================================================================
    
    def run_complete_workflow(
        self,
        initial_student_message: Optional[str] = None,
        discussion_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run the complete teaching workflow from start to finish
        
        Args:
            initial_student_message: Optional first message from student after syllabus
            discussion_callback: Optional callback for discussion updates
            
        Returns:
            Dictionary with all artifacts and results
        """
        self.logger.info("#" * 60)
        self.logger.info("RUNNING COMPLETE EDUGPT WORKFLOW")
        self.logger.info(f"Topic: {self.topic}")
        self.logger.info("#" * 60)
        
        # Step 1: Setup
        self.setup()
        
        # Step 2: Generate Syllabus
        syllabus = self.generate_syllabus(discussion_callback)
        
        # Step 3: Start Teaching
        opening = self.start_teaching()
        
        # Optional: Handle first student interaction
        first_response = None
        if initial_student_message:
            first_response = self.teach_interaction(initial_student_message)
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("WORKFLOW COMPLETE - READY FOR INTERACTIVE TEACHING")
        self.logger.info("=" * 60)
        
        return {
            "topic": self.topic,
            "discussion_history": self.discussion_history,
            "syllabus": syllabus,
            "instructor_opening": opening,
            "first_interaction": {
                "student": initial_student_message,
                "instructor": first_response
            } if initial_student_message else None,
            "output_dir": str(self.output_dir) if self.save_artifacts else None
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize topic name for use in filenames"""
        return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of the orchestrator"""
        return {
            "topic": self.topic,
            "discussion_complete": self.discussion_complete,
            "syllabus_generated": self.syllabus_generated,
            "teaching_active": self.teaching_active,
            "has_discussion": self.discussion_history is not None,
            "has_syllabus": self.syllabus is not None,
            "has_instructor": self.instructor is not None
        }
    
    def export_all_artifacts(self, export_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Export all artifacts to files
        
        Args:
            export_dir: Optional custom export directory
            
        Returns:
            Dictionary mapping artifact types to file paths
        """
        export_path = Path(export_dir) if export_dir else self.output_dir
        export_path.mkdir(parents=True, exist_ok=True)
        
        artifacts = {}
        
        # Export discussion
        if self.discussion_history:
            file_path = export_path / f"{self._sanitize_filename(self.topic)}_discussion.txt"
            with open(file_path, 'w') as f:
                f.write(self.discussion_history)
            artifacts["discussion"] = str(file_path)
        
        # Export syllabus
        if self.syllabus:
            file_path = export_path / f"{self._sanitize_filename(self.topic)}_syllabus.md"
            with open(file_path, 'w') as f:
                f.write(f"# {self.topic}\n\n{self.syllabus}")
            artifacts["syllabus"] = str(file_path)
        
        # Export state
        state_file = export_path / f"{self._sanitize_filename(self.topic)}_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.get_state(), f, indent=2)
        artifacts["state"] = str(state_file)
        
        self.logger.info(f"Exported {len(artifacts)} artifacts to {export_path}")
        
        return artifacts