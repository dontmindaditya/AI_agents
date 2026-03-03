"""
Research Agent - Gathers information from various sources
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import Optional
import os


def create_researcher_agent(llm: Optional[ChatOpenAI] = None) -> Agent:
    """
    Create the researcher agent
    
    Args:
        llm: Optional language model instance
        
    Returns:
        Configured researcher agent
    """
    if llm is None:
        llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
            temperature=0.7
        )
    
    return Agent(
        role="Senior Research Analyst",
        goal="Conduct comprehensive research on given topics and gather accurate, relevant information from multiple sources",
        backstory="""You are an experienced research analyst with a keen eye for detail and accuracy.
        You excel at finding relevant information, validating sources, and synthesizing complex data into clear insights.
        You always verify facts from multiple sources and prioritize authoritative references.
        When conducting research, you consider multiple perspectives and look for the most recent and reliable information.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_pdf_researcher_agent(llm: Optional[ChatOpenAI] = None) -> Agent:
    """
    Create the PDF research agent specialized in document analysis
    
    Args:
        llm: Optional language model instance
        
    Returns:
        Configured PDF researcher agent
    """
    if llm is None:
        llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
            temperature=0.7
        )
    
    return Agent(
        role="Document Analysis Specialist",
        goal="Extract and analyze information from PDF documents and research papers",
        backstory="""You are a specialist in analyzing academic papers, research documents, and technical reports.
        You excel at understanding complex documents, extracting key information, identifying methodologies,
        and synthesizing findings. You can quickly grasp the main contributions of research papers and
        identify important details that others might miss.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )