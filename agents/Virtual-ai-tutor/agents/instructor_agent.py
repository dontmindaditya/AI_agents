"""
Instructor Agent - Teaches students based on the generated syllabus
"""

from typing import Optional, Dict, Any, List
from langchain_core.language_models.base import BaseLanguageModel
from agents.base_agent import ConversationalAgent
from config.prompts import prompts
from models.llm_provider import create_instructor_llm


class InstructorAgent(ConversationalAgent):
    """
    Instructor Agent that teaches students following the syllabus
    
    Provides adaptive, personalized instruction based on:
    - The generated syllabus
    - Student's progress and understanding
    - Student's questions and responses
    """
    
    def __init__(
        self,
        topic: str,
        syllabus: str,
        llm: Optional[BaseLanguageModel] = None,
        **kwargs
    ):
        """
        Initialize the Instructor Agent
        
        Args:
            topic: The learning topic
            syllabus: Generated syllabus to follow
            llm: Optional pre-configured LLM
            **kwargs: Additional configuration
        """
        self.topic = topic
        self.syllabus = syllabus
        
        # Extract first module from syllabus
        self.current_module = self._extract_first_module(syllabus)
        self.progress = "0% - Just starting"
        
        # Format system prompt
        system_prompt = prompts.INSTRUCTOR_SYSTEM.format(
            topic=topic,
            syllabus=syllabus,
            current_module=self.current_module,
            progress=self.progress
        )
        
        # Use instructor-optimized LLM if not provided
        llm = llm or create_instructor_llm()
        
        super().__init__(
            name="InstructorAgent",
            system_prompt=system_prompt,
            llm=llm,
            temperature=0.7,
            max_tokens=2000,
            **kwargs
        )
        
        # Teaching state
        self.modules_covered: List[str] = []
        self.student_questions: List[str] = []
        self.assessments: List[Dict[str, Any]] = []
        self.teaching_session_active = False
    
    def _extract_first_module(self, syllabus: str) -> str:
        """Extract the first module/section from the syllabus"""
        # Simple extraction - look for first numbered section or heading
        lines = syllabus.split('\n')
        for line in lines:
            if line.strip() and any(c.isdigit() for c in line[:5]):
                return line.strip()
        return "Introduction and Fundamentals"
    
    def start_teaching_session(self) -> str:
        """
        Start a teaching session with an introduction
        
        Returns:
            Opening message to the student
        """
        self.teaching_session_active = True
        self.start_conversation({"topic": self.topic})
        
        # Get syllabus overview for introduction
        syllabus_overview = self._get_syllabus_overview()
        
        # Generate opening message
        opening = prompts.INSTRUCTOR_INITIAL_MESSAGE.format(
            topic=self.topic,
            syllabus_overview=syllabus_overview,
            first_module=self.current_module
        )
        
        # Get personalized opening from LLM
        personalized_opening = self.get_response(
            opening,
            include_history=False,
            add_to_history=True
        )
        
        self.logger.info(f"Started teaching session on: {self.topic}")
        return personalized_opening
    
    def _get_syllabus_overview(self) -> str:
        """Get a brief overview of the syllabus"""
        # Return first ~500 characters or first few lines
        lines = self.syllabus.split('\n')[:10]
        return '\n'.join(lines)
    
    def teach(self, student_message: str) -> str:
        """
        Respond to student's message with teaching content
        
        Args:
            student_message: Student's question or response
            
        Returns:
            Instructor's teaching response
        """
        if not self.teaching_session_active:
            raise ValueError("Teaching session not started. Call start_teaching_session() first.")
        
        # Record student question/response
        self.student_questions.append(student_message)
        
        # Prepare teaching prompt
        teaching_prompt = prompts.INSTRUCTOR_TEACHING_PROMPT.format(
            student_message=student_message
        )
        
        # Get response
        response = self.get_response(student_message, include_history=True)
        
        self.logger.info(f"Responded to student ({len(response)} chars)")
        
        return response
    
    def update_progress(self, module: str, progress_percentage: int):
        """
        Update current module and progress
        
        Args:
            module: Current module being taught
            progress_percentage: Progress percentage (0-100)
        """
        self.current_module = module
        self.progress = f"{progress_percentage}% - {module}"
        
        if module not in self.modules_covered:
            self.modules_covered.append(module)
        
        # Update system prompt with new progress
        updated_prompt = prompts.INSTRUCTOR_SYSTEM.format(
            topic=self.topic,
            syllabus=self.syllabus,
            current_module=self.current_module,
            progress=self.progress
        )
        self.update_system_prompt(updated_prompt)
        
        self.logger.info(f"Updated progress: {self.progress}")
    
    def assess_understanding(self, interaction_history: Optional[str] = None) -> Dict[str, Any]:
        """
        Assess student's understanding based on interactions
        
        Args:
            interaction_history: Optional custom history to assess
            
        Returns:
            Assessment results
        """
        # Prepare interaction history
        if not interaction_history:
            interaction_history = self._format_interaction_history()
        
        # Generate assessment prompt
        assessment_prompt = prompts.ASSESSMENT_PROMPT.format(
            topic=self.topic,
            interaction_history=interaction_history
        )
        
        # Get assessment
        assessment = self.get_response(
            assessment_prompt,
            include_history=False,
            add_to_history=False
        )
        
        # Store assessment
        assessment_record = {
            "timestamp": self.logger.name,
            "content": assessment,
            "modules_covered": self.modules_covered.copy()
        }
        self.assessments.append(assessment_record)
        
        self.logger.info("Generated student assessment")
        
        return {
            "assessment": assessment,
            "modules_covered": len(self.modules_covered),
            "questions_asked": len(self.student_questions)
        }
    
    def _format_interaction_history(self) -> str:
        """Format conversation history for assessment"""
        formatted = []
        for msg in self.message_history[-10:]:  # Last 10 messages
            role = "Student" if msg["role"] == "user" else "Instructor"
            formatted.append(f"{role}: {msg['content'][:200]}...")
        return "\n\n".join(formatted)
    
    def provide_feedback(self, student_work: str) -> str:
        """
        Provide feedback on student's work
        
        Args:
            student_work: Student's work to evaluate
            
        Returns:
            Detailed feedback
        """
        feedback_prompt = f"""Please provide constructive feedback on this student's work:

{student_work}

Consider:
1. Understanding of concepts
2. Accuracy and correctness
3. Areas for improvement
4. Encouragement and next steps

Provide detailed, supportive feedback:"""
        
        feedback = self.get_response(
            feedback_prompt,
            include_history=True,
            add_to_history=True
        )
        
        return feedback
    
    def suggest_exercises(self, module: Optional[str] = None) -> str:
        """
        Suggest practice exercises
        
        Args:
            module: Specific module to suggest exercises for
            
        Returns:
            Suggested exercises
        """
        module = module or self.current_module
        
        exercise_prompt = f"""Based on the syllabus and our current progress on "{module}", 
suggest 3-5 practical exercises or projects that would help reinforce the concepts.

For each exercise, provide:
1. Title and brief description
2. Difficulty level
3. Key concepts it reinforces
4. Estimated time to complete

Suggested exercises:"""
        
        exercises = self.get_response(
            exercise_prompt,
            include_history=False,
            add_to_history=False
        )
        
        return exercises
    
    def answer_question(self, question: str, detailed: bool = True) -> str:
        """
        Answer a specific student question
        
        Args:
            question: Student's question
            detailed: Whether to provide detailed explanation
            
        Returns:
            Answer to the question
        """
        if detailed:
            question_prompt = f"""Student asks: {question}

Please provide a detailed, clear explanation that:
1. Directly answers the question
2. Provides examples where helpful
3. Relates to the current module: {self.current_module}
4. Checks if further clarification is needed

Your answer:"""
        else:
            question_prompt = question
        
        answer = self.get_response(question_prompt, include_history=True)
        return answer
    
    def end_teaching_session(self) -> Dict[str, Any]:
        """
        End the teaching session and provide summary
        
        Returns:
            Session summary
        """
        self.teaching_session_active = False
        
        summary = {
            "topic": self.topic,
            "modules_covered": self.modules_covered,
            "total_interactions": len(self.message_history),
            "questions_asked": len(self.student_questions),
            "assessments_conducted": len(self.assessments),
            "final_progress": self.progress
        }
        
        self.logger.info(f"Ended teaching session. Summary: {summary}")
        
        return summary
    
    def process(self, student_message: str, **kwargs) -> str:
        """
        Main processing method - teach based on student message
        
        Args:
            student_message: Message from student
            **kwargs: Additional parameters
            
        Returns:
            Teaching response
        """
        return self.teach(student_message)
    
    def get_session_summary(self) -> str:
        """Get a formatted summary of the teaching session"""
        summary = self.end_teaching_session()
        
        formatted = f"""
Teaching Session Summary
========================
Topic: {summary['topic']}
Modules Covered: {', '.join(summary['modules_covered']) or 'None yet'}
Total Interactions: {summary['total_interactions']}
Questions Asked: {summary['questions_asked']}
Progress: {summary['final_progress']}
"""
        return formatted