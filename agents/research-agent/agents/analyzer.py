"""
Analyzer Agent - Analyzes and synthesizes research findings
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import Optional
import os


def create_analyzer_agent(llm: Optional[ChatOpenAI] = None) -> Agent:
    """
    Create the analyzer agent
    
    Args:
        llm: Optional language model instance
        
    Returns:
        Configured analyzer agent
    """
    if llm is None:
        llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
            temperature=0.7
        )
    
    return Agent(
        role="Content Analysis Specialist",
        goal="Analyze and synthesize research findings into structured insights",
        backstory="""You are a specialist in content analysis with expertise in identifying key themes,
        patterns, and insights from large volumes of information. You excel at breaking down complex topics
        into digestible components and highlighting the most important findings.
        
        Your analysis always includes:
        - Main themes and key points
        - Supporting evidence and data
        - Different perspectives and viewpoints
        - Patterns and trends
        - Critical insights and implications
        
        You organize information logically and ensure nothing important is overlooked.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )