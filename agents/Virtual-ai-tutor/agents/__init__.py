"""
Agents package for EduGPT AI Instructor
"""

from .base_agent import BaseAgent
from .discussion_agents import DiscussionAgent, Agent1, Agent2
from .syllabus_generator import SyllabusGenerator
from .instructor_agent import InstructorAgent

__all__ = [
    'BaseAgent',
    'DiscussionAgent',
    'Agent1',
    'Agent2',
    'SyllabusGenerator',
    'InstructorAgent'
]