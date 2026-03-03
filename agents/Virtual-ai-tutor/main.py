"""
Main entry point for EduGPT AI Instructor
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from orchestrator import TeachingOrchestrator
from config.settings import settings
from utils.logger import setup_logger


console = Console()


def print_header():
    """Print application header"""
    header = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║             🎓 EduGPT AI Instructor System 🎓             ║
║                                                           ║
║          Personalized AI-Powered Learning Platform        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    console.print(header, style="bold blue")


def interactive_teaching_session(orchestrator: TeachingOrchestrator):
    """Run interactive teaching session"""
    console.print("\n[bold green]Teaching Session Started![/bold green]")
    console.print("[yellow]Type 'exit' or 'quit' to end the session[/yellow]")
    console.print("[yellow]Type 'assess' to get an assessment of your understanding[/yellow]")
    console.print("[yellow]Type 'summary' to see session summary[/yellow]\n")
    
    # Get opening message
    opening = orchestrator.start_teaching()
    console.print(Panel(opening, title="[bold]Instructor[/bold]", border_style="green"))
    
    # Interactive loop
    while True:
        try:
            # Get student input
            student_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()
            
            if not student_input:
                continue
            
            # Check for special commands
            if student_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[yellow]Ending teaching session...[/yellow]")
                break
            
            elif student_input.lower() == 'assess':
                console.print("\n[bold]Assessing your understanding...[/bold]")
                assessment = orchestrator.assess_student()
                console.print(Panel(
                    assessment['assessment'],
                    title="[bold]Assessment Results[/bold]",
                    border_style="blue"
                ))
                continue
            
            elif student_input.lower() == 'summary':
                summary = orchestrator.instructor.get_session_summary()
                console.print(Panel(summary, title="[bold]Session Summary[/bold]", border_style="yellow"))
                continue
            
            # Get instructor response
            response = orchestrator.teach_interaction(student_input)
            console.print(Panel(response, title="[bold]Instructor[/bold]", border_style="green"))
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Session interrupted. Ending...[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
    
    # End session
    summary = orchestrator.end_teaching()
    console.print("\n[bold green]Session Summary:[/bold green]")
    console.print(f"  • Modules Covered: {len(summary['modules_covered'])}")
    console.print(f"  • Total Interactions: {summary['total_interactions']}")
    console.print(f"  • Questions Asked: {summary['questions_asked']}")


def run_workflow(
    topic: str,
    output_dir: str = "./outputs",
    interactive: bool = True,
    discussion_rounds: int = 5
):
    """
    Run the complete EduGPT workflow
    
    Args:
        topic: Learning topic
        output_dir: Directory to save outputs
        interactive: Whether to run interactive teaching session
        discussion_rounds: Number of discussion rounds
    """
    console.print(f"\n[bold]Learning Topic:[/bold] {topic}")
    console.print(f"[bold]Discussion Rounds:[/bold] {discussion_rounds}")
    console.print(f"[bold]Output Directory:[/bold] {output_dir}\n")
    
    # Initialize orchestrator
    orchestrator = TeachingOrchestrator(
        topic=topic,
        max_discussion_rounds=discussion_rounds,
        save_artifacts=True,
        output_dir=output_dir
    )
    
    # Define discussion callback for progress updates
    def discussion_progress(round_num: int, agent: str, message: str):
        agent_name = "Agent 1" if agent == "agent1" else "Agent 2"
        console.print(f"[dim]Round {round_num} - {agent_name} responded[/dim]")
    
    try:
        # Run workflow
        with console.status("[bold green]Running EduGPT workflow...", spinner="dots"):
            console.print("\n[bold yellow]Step 1:[/bold yellow] Initializing agents...")
            orchestrator.setup()
            
            console.print("[bold yellow]Step 2:[/bold yellow] Generating syllabus through agent discussion...")
            orchestrator.generate_syllabus(discussion_callback=discussion_progress)
        
        console.print("\n[bold green]✓ Syllabus generated successfully![/bold green]")
        
        # Display syllabus
        console.print("\n" + "=" * 60)
        console.print(Panel(
            Markdown(orchestrator.syllabus),
            title=f"[bold]Generated Syllabus: {topic}[/bold]",
            border_style="cyan"
        ))
        console.print("=" * 60)
        
        # Interactive teaching if requested
        if interactive:
            console.print("\n[bold yellow]Step 3:[/bold yellow] Starting interactive teaching session...")
            interactive_teaching_session(orchestrator)
        else:
            console.print("\n[bold yellow]Step 3:[/bold yellow] Teaching session ready (non-interactive mode)")
            opening = orchestrator.start_teaching()
            console.print(Panel(opening, title="[bold]Instructor Opening[/bold]", border_style="green"))
        
        # Export artifacts
        artifacts = orchestrator.export_all_artifacts()
        console.print("\n[bold green]✓ Workflow complete![/bold green]")
        console.print(f"\n[bold]Artifacts saved to:[/bold] {output_dir}")
        for artifact_type, path in artifacts.items():
            console.print(f"  • {artifact_type}: {Path(path).name}")
        
    except Exception as e:
        console.print(f"\n[bold red]Error during workflow:[/bold red] {str(e)}")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="EduGPT AI Instructor - Personalized AI-Powered Learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with interactive teaching
  python main.py "Reinforcement Learning"
  
  # Custom discussion rounds
  python main.py "Deep Learning" --rounds 7
  
  # Non-interactive mode (just generate syllabus)
  python main.py "Natural Language Processing" --no-interactive
  
  # Custom output directory
  python main.py "Computer Vision" --output ./my_outputs
        """
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="Learning topic to teach"
    )
    
    parser.add_argument(
        "-r", "--rounds",
        type=int,
        default=5,
        help="Number of discussion rounds for syllabus generation (default: 5)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./outputs",
        help="Output directory for saving artifacts (default: ./outputs)"
    )
    
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Run in non-interactive mode (no teaching session)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        settings.log_level = "DEBUG"
    
    # Validate API keys
    try:
        settings.validate_api_keys()
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("\n[yellow]Please set at least one API key in your .env file:[/yellow]")
        console.print("  OPENAI_API_KEY=your_key")
        console.print("  ANTHROPIC_API_KEY=your_key")
        console.print("  GOOGLE_API_KEY=your_key")
        sys.exit(1)
    
    # Print header
    print_header()
    
    # Run workflow
    try:
        run_workflow(
            topic=args.topic,
            output_dir=args.output,
            interactive=not args.no_interactive,
            discussion_rounds=args.rounds
        )
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Fatal error:[/bold red] {str(e)}")
        if args.verbose:
            import traceback
            console.print("\n[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()