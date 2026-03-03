"""
Main entry point for Paper2Code Agent System
"""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

from agents import Paper2CodeOrchestrator, quick_convert
from config import settings
from utils.logger import logger, log_success, log_error
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Load environment variables
load_dotenv()

console = Console()


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              📄 PAPER2CODE AGENT SYSTEM 🤖                ║
    ║                                                           ║
    ║          Transform Research Papers into Code             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def print_results(code_output):
    """Print conversion results in a nice table"""
    
    # Create summary table
    table = Table(title="Conversion Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Language", code_output.language.value.upper())
    table.add_row("Code Files", str(len(code_output.code_files)))
    table.add_row("Test Files", str(len(code_output.test_files)))
    table.add_row("Total Lines", str(code_output.total_lines))
    table.add_row("Quality", code_output.review_result.quality_score.value if code_output.review_result else "N/A")
    table.add_row("Generation Time", f"{code_output.generation_time:.2f}s" if code_output.generation_time else "N/A")
    
    console.print(table)
    
    # Print files generated
    if code_output.code_files:
        console.print("\n[bold]Generated Files:[/bold]")
        for file in code_output.code_files:
            console.print(f"  ✓ {file.file_name} ({file.line_count} lines)")
    
    if code_output.test_files:
        console.print("\n[bold]Test Files:[/bold]")
        for file in code_output.test_files:
            console.print(f"  ✓ {file.file_name} ({file.test_count} tests)")


def convert_command(args):
    """Handle convert command"""
    print_banner()
    
    console.print(f"\n[bold]Converting paper:[/bold] {args.paper}")
    console.print(f"[bold]Language:[/bold] {args.language}")
    console.print(f"[bold]Output:[/bold] {args.output}\n")
    
    try:
        # Run conversion
        code_output = quick_convert(
            paper_path=args.paper,
            output_dir=args.output,
            language=args.language
        )
        
        # Print results
        print_results(code_output)
        
        log_success(logger, f"\n✨ Code generated successfully in {args.output}")
        
        return 0
    
    except Exception as e:
        log_error(logger, f"Conversion failed: {str(e)}", exc=e)
        return 1


def interactive_mode(args):
    """Interactive mode for paper conversion"""
    print_banner()
    
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("Convert research papers or algorithm descriptions to code\n")
    
    # Ask what type of input
    console.print("[bold]What would you like to convert?[/bold]")
    console.print("  1. PDF Research Paper")
    console.print("  2. Algorithm Description (Text)")
    console.print()
    
    choice = console.input("[bold]Enter choice (1 or 2):[/bold] ").strip()
    
    if choice == "1":
        # PDF Path Input
        console.print("\n[bold cyan]PDF Conversion Mode[/bold cyan]\n")
        
        pdf_path = console.input("[bold]📄 PDF File Path:[/bold] ").strip().strip('"').strip("'")
        
        if not pdf_path:
            console.print("[red]No file path provided[/red]")
            return 1
        
        # Check if file exists
        if not Path(pdf_path).exists():
            console.print(f"\n[red]❌ Error: PDF not found![/red]")
            console.print(f"   Looking for: {pdf_path}")
            console.print(f"   Current directory: {Path.cwd()}")
            console.print("\n[yellow]Tip: Use absolute path like:[/yellow]")
            console.print("   Windows: D:\\papers\\research.pdf")
            console.print("   Linux/Mac: /home/user/papers/research.pdf")
            return 1
        
        # Check if it's actually a PDF
        if not pdf_path.lower().endswith('.pdf'):
            console.print(f"\n[yellow]⚠️  Warning: File doesn't have .pdf extension[/yellow]")
            continue_anyway = console.input("Continue anyway? (y/n): ").strip().lower()
            if continue_anyway != 'y':
                console.print("[red]Conversion cancelled[/red]")
                return 1
        
        paper_input = pdf_path
        is_file = True
        
        console.print(f"\n[green]✓ PDF found: {Path(pdf_path).name}[/green]")
        
    elif choice == "2":
        # Text Description Input
        console.print("\n[bold cyan]Text Description Mode[/bold cyan]\n")
        console.print("[bold]Enter algorithm description:[/bold]")
        console.print("[dim](Press Enter twice when done)[/dim]\n")
        
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        paper_input = '\n'.join(lines).strip()
        
        if not paper_input:
            console.print("[red]No description provided[/red]")
            return 1
        
        is_file = False
        
        console.print(f"\n[green]✓ Description received ({len(paper_input)} characters)[/green]")
        
    else:
        console.print("[red]Invalid choice. Please enter 1 or 2[/red]")
        return 1
    
    # Get language with better validation
    console.print("\n[bold]Programming Language:[/bold]")
    console.print("  Options: python, javascript, typescript, java, cpp")
    language_input = console.input("[bold]Language (press Enter for python):[/bold] ").strip().lower()
    
    # Clean language input - remove common prefixes
    language_input = language_input.replace("language:", "").replace("language", "").strip()
    
    # Validate and default
    valid_languages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'go', 'rust']
    language = language_input if language_input in valid_languages else "python"
    
    if language_input and language_input not in valid_languages:
        console.print(f"[yellow]Warning: '{language_input}' not recognized, using 'python'[/yellow]")
    
    # Get output directory
    console.print("\n[bold]Output Directory:[/bold]")
    output_input = console.input("[bold]Directory (press Enter for ./output):[/bold] ").strip()
    output_input = output_input.replace("output directory:", "").replace("output:", "").strip()
    output_dir = output_input if output_input else "./output"
    
    # Show configuration summary
    console.print("\n" + "="*60)
    console.print("[bold cyan]Configuration Summary[/bold cyan]")
    console.print("="*60)
    if is_file:
        console.print(f"  📄 Input:    PDF file")
        console.print(f"  📂 File:     {Path(paper_input).name}")
        console.print(f"  📁 Location: {Path(paper_input).parent}")
    else:
        console.print(f"  📝 Input:    Text description")
        console.print(f"  📏 Length:   {len(paper_input)} characters")
    console.print(f"  💻 Language: {language}")
    console.print(f"  📦 Output:   {output_dir}")
    console.print("="*60 + "\n")
    
    # Confirm
    confirm = console.input("[bold]Start conversion? (Y/n):[/bold] ").strip().lower()
    if confirm and confirm not in ['y', 'yes']:
        console.print("[yellow]Conversion cancelled[/yellow]")
        return 0
    
    console.print("\n[bold green]🚀 Starting conversion...[/bold green]\n")
    
    try:
        orchestrator = Paper2CodeOrchestrator(
            progress_callback=lambda stage, msg: console.print(f"[cyan]{stage}:[/cyan] {msg}")
        )
        
        if is_file:
            code_output = orchestrator.convert_paper_to_code(
                paper_path=paper_input,
                language=language,
                output_dir=output_dir
            )
        else:
            code_output = orchestrator.convert_from_text(
                paper_text=paper_input,
                language=language,
                output_dir=output_dir
            )
        
        print_results(code_output)
        log_success(logger, f"\n✨ Code generated successfully in {output_dir}")
        
        return 0
    
    except Exception as e:
        log_error(logger, f"Conversion failed: {str(e)}", exc=e)
        return 1


def info_command(args):
    """Show system information"""
    print_banner()
    
    orchestrator = Paper2CodeOrchestrator()
    status = orchestrator.get_status()
    
    # System info
    info_table = Table(title="System Information", show_header=False)
    info_table.add_column("Setting", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("LLM Provider", settings.primary_llm_provider.upper())
    info_table.add_row("Default Language", settings.default_language.upper())
    info_table.add_row("Max Iterations", str(settings.max_iterations))
    info_table.add_row("Verbose Mode", str(settings.verbose))
    info_table.add_row("Generate Tests", str(settings.include_tests))
    info_table.add_row("Generate Docs", str(settings.include_docs))
    
    console.print(info_table)
    
    # Agent status
    console.print("\n[bold]Agent Status:[/bold]")
    for agent_name, is_ready in status['agents'].items():
        status_icon = "✓" if is_ready else "✗"
        status_color = "green" if is_ready else "red"
        console.print(f"  [{status_color}]{status_icon}[/{status_color}] {agent_name.replace('_', ' ').title()}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Paper2Code - Transform research papers into working code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a PDF paper to Python code
  python main.py convert paper.pdf -o ./output -l python
  
  # Interactive mode
  python main.py interactive
  
  # Show system info
  python main.py info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert paper to code')
    convert_parser.add_argument('paper', help='Path to PDF paper or text file')
    convert_parser.add_argument('-o', '--output', default='./output', help='Output directory')
    convert_parser.add_argument('-l', '--language', default='python', 
                              choices=['python', 'javascript', 'typescript', 'java', 'cpp'],
                              help='Programming language')
    convert_parser.add_argument('-f', '--framework', help='Framework (e.g., pytorch, tensorflow)')
    convert_parser.add_argument('--no-tests', action='store_true', help='Skip test generation')
    convert_parser.add_argument('--no-docs', action='store_true', help='Skip documentation')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show system information')
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'convert':
        return convert_command(args)
    elif args.command == 'interactive':
        return interactive_mode(args)
    elif args.command == 'info':
        info_command(args)
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())