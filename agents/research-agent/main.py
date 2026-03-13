"""
Main entry point for the Research Agent System

This system supports two modes:
1. Text prompt research - Research any topic via text input
2. PDF analysis - Upload and analyze PDF documents
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from crewai import Crew, Task
from langchain_openai import ChatOpenAI

from agents import (
    create_researcher_agent,
    create_pdf_researcher_agent,
    create_analyzer_agent,
    create_writer_agent
)

from tools import read_pdf, create_search_tool
from utils import (
    ensure_directories,
    save_report,
    print_header,
    print_success,
    print_error,
    print_info,
    validate_env_variables,
    RESEARCH_TASK_DESCRIPTION,
    ANALYSIS_TASK_DESCRIPTION,
    WRITING_TASK_DESCRIPTION,
    PDF_ANALYSIS_TASK_DESCRIPTION
)

# Load environment variables from root .env
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")


class ResearchAgent:
    """Main research agent orchestrator"""
    
    def __init__(self):
        """Initialize the research agent system"""
        # Validate environment
        if not validate_env_variables():
            sys.exit(1)
        
        # Ensure directories exist
        ensure_directories()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            temperature=0.7
        )
        
        print_success("Research Agent System initialized successfully!")
    
    def research_from_prompt(self, topic: str) -> str:
        """
        Conduct research based on a text prompt
        
        Args:
            topic: Research topic or question
            
        Returns:
            Generated research report
        """
        print_header(f"Starting Research on: {topic}")
        
        # Create agents
        researcher = create_researcher_agent(self.llm)
        analyzer = create_analyzer_agent(self.llm)
        writer = create_writer_agent(self.llm)
        
        # Create tasks
        research_task = Task(
            description=RESEARCH_TASK_DESCRIPTION.format(
                topic=topic,
                additional_context="Use web search if needed to find the most current information."
            ),
            agent=researcher,
            expected_output="Comprehensive research findings with sources and key information"
        )
        
        analysis_task = Task(
            description=ANALYSIS_TASK_DESCRIPTION.format(topic=topic),
            agent=analyzer,
            expected_output="Structured analysis with main themes, insights, and organized findings"
        )
        
        writing_task = Task(
            description=WRITING_TASK_DESCRIPTION.format(topic=topic),
            agent=writer,
            expected_output="Professional research report in markdown format with all sections"
        )
        
        # Create crew
        crew = Crew(
            agents=[researcher, analyzer, writer],
            tasks=[research_task, analysis_task, writing_task],
            verbose=True
        )
        
        # Execute research
        print_info("Research crew is working...")
        result = crew.kickoff()
        
        return str(result)
    
    def research_from_pdf(self, pdf_path: str) -> str:
        """
        Analyze and research based on PDF content
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Generated research report
        """
        print_header(f"Analyzing PDF: {Path(pdf_path).name}")
        
        # Extract PDF content
        print_info("Extracting PDF content...")
        try:
            pdf_data = read_pdf(pdf_path)
            pdf_content = pdf_data['content']
            
            if not pdf_content or len(pdf_content.strip()) < 100:
                print_error("Failed to extract meaningful content from PDF")
                return ""
            
            print_success(f"Extracted {len(pdf_content)} characters from PDF")
            
        except Exception as e:
            print_error(f"PDF extraction failed: {str(e)}")
            return ""
        
        # Create agents
        pdf_researcher = create_pdf_researcher_agent(self.llm)
        analyzer = create_analyzer_agent(self.llm)
        writer = create_writer_agent(self.llm)
        
        # Create tasks
        pdf_analysis_task = Task(
            description=PDF_ANALYSIS_TASK_DESCRIPTION.format(
                pdf_content=pdf_content[:8000]  # Limit content length
            ),
            agent=pdf_researcher,
            expected_output="Comprehensive analysis of the PDF document with key findings"
        )
        
        synthesis_task = Task(
            description=f"""Based on the PDF analysis, synthesize the information and provide:
            1. Executive summary of the document
            2. Main contributions and findings
            3. Methodology or approach used
            4. Key data points and statistics
            5. Implications and significance
            
            Organize the information logically and highlight the most important aspects.""",
            agent=analyzer,
            expected_output="Structured synthesis of PDF content with organized insights"
        )
        
        report_task = Task(
            description=f"""Create a comprehensive report about the analyzed PDF document.
            
            The report should include:
            - Document overview
            - Main findings and contributions
            - Detailed analysis
            - Key takeaways
            - References to important sections
            
            Format the output in professional markdown.""",
            agent=writer,
            expected_output="Professional PDF analysis report in markdown format"
        )
        
        # Create crew
        crew = Crew(
            agents=[pdf_researcher, analyzer, writer],
            tasks=[pdf_analysis_task, synthesis_task, report_task],
            verbose=True
        )
        
        # Execute analysis
        print_info("Analysis crew is working...")
        result = crew.kickoff()
        
        return str(result)


def display_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("🔬 RESEARCH AGENT SYSTEM")
    print("="*60)
    print("\nChoose an option:")
    print("  1. Research a topic (text prompt)")
    print("  2. Analyze a PDF document")
    print("  3. Exit")
    print("\n" + "="*60)


def get_user_choice() -> str:
    """Get user's menu choice"""
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print_error("Invalid choice. Please enter 1, 2, or 3.")


def get_research_topic() -> str:
    """Get research topic from user"""
    print("\n" + "-"*60)
    print("📝 Enter your research topic or question:")
    print("-"*60)
    topic = input("\n> ").strip()
    
    if not topic:
        print_error("Topic cannot be empty!")
        return get_research_topic()
    
    return topic


def get_pdf_path() -> str:
    """Get PDF file path from user"""
    print("\n" + "-"*60)
    print("📄 Enter the path to your PDF file:")
    print("-"*60)
    print("(You can drag and drop the file here)")
    
    pdf_path = input("\n> ").strip().strip('"').strip("'")
    
    if not pdf_path:
        print_error("Path cannot be empty!")
        return get_pdf_path()
    
    if not os.path.exists(pdf_path):
        print_error(f"File not found: {pdf_path}")
        return get_pdf_path()
    
    if not pdf_path.lower().endswith('.pdf'):
        print_error("File must be a PDF!")
        return get_pdf_path()
    
    return pdf_path


def main():
    """Main application loop"""
    print_header("Welcome to the Research Agent System!")
    
    # Initialize research agent
    try:
        agent = ResearchAgent()
    except Exception as e:
        print_error(f"Failed to initialize: {str(e)}")
        sys.exit(1)
    
    while True:
        display_menu()
        choice = get_user_choice()
        
        if choice == '1':
            # Text prompt research
            topic = get_research_topic()
            
            try:
                result = agent.research_from_prompt(topic)
                
                if result:
                    # Save report
                    filename = f"research_{topic[:30].replace(' ', '_')}.md"
                    filepath = save_report(result, filename)
                    
                    print_success(f"\n✅ Research complete!")
                    print_success(f"📄 Report saved to: {filepath}")
                else:
                    print_error("Research failed to generate a report")
            
            except Exception as e:
                print_error(f"Research failed: {str(e)}")
        
        elif choice == '2':
            # PDF analysis
            pdf_path = get_pdf_path()
            
            try:
                result = agent.research_from_pdf(pdf_path)
                
                if result:
                    # Save report
                    pdf_name = Path(pdf_path).stem
                    filename = f"pdf_analysis_{pdf_name}.md"
                    filepath = save_report(result, filename)
                    
                    print_success(f"\n✅ Analysis complete!")
                    print_success(f"📄 Report saved to: {filepath}")
                else:
                    print_error("PDF analysis failed to generate a report")
            
            except Exception as e:
                print_error(f"PDF analysis failed: {str(e)}")
        
        elif choice == '3':
            print_info("\nThank you for using Research Agent System! Goodbye! 👋")
            break
        
        # Ask if user wants to continue
        print("\n" + "-"*60)
        continue_choice = input("Do you want to perform another operation? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print_info("\nThank you for using Research Agent System! Goodbye! 👋")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\nOperation cancelled by user. Goodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)