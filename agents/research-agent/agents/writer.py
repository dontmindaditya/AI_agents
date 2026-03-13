"""
Writer Agent - Creates comprehensive research reports
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import Optional
import os


def create_writer_agent(llm: Optional[ChatOpenAI] = None) -> Agent:
    """
    Create the writer agent
    
    Args:
        llm: Optional language model instance
        
    Returns:
        Configured writer agent
    """
    if llm is None:
        llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            temperature=0.7
        )
    
    return Agent(
        role="Technical Writer",
        goal="Create clear, comprehensive research reports that are well-structured and easy to understand",
        backstory="""You are a professional technical writer with years of experience in creating
        research reports and documentation. You excel at presenting complex information in a clear,
        logical, and engaging manner. Your reports are always well-organized with proper citations.
        
        Your writing style includes:
        - Clear, concise language
        - Logical structure with proper headings
        - Executive summaries for quick understanding
        - Well-formatted markdown output
        - Proper citations and references
        - Key takeaways and actionable insights
        
        You ensure that reports are accessible to both technical and non-technical readers while
        maintaining accuracy and depth.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )